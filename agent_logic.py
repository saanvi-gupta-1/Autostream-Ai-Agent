import os
from typing import TypedDict, Literal
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from intent import (
    Intent, classify_intent, extract_lead_info, calculate_lead_score,
    get_score_label, detect_topic, _detect_platform_in_text,
)
from rag_pipeline import retrieve_context, get_full_knowledge_base_text
from tools import mock_lead_capture, validate_email, validate_name


# ─── Cache KB text to avoid re-reading file every turn ───
_kb_text_cache: str | None = None


def _get_kb_text() -> str:
    global _kb_text_cache
    if _kb_text_cache is None:
        _kb_text_cache = get_full_knowledge_base_text()
    return _kb_text_cache


class AgentState(TypedDict):
    messages: list[dict]
    intent: str
    lead_score: int
    collecting_lead_info: bool
    lead_name: str | None
    lead_email: str | None
    lead_platform: str | None
    lead_captured: bool
    rag_context: str
    user_platform: str | None
    last_topic: str | None


def _get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=300,
    )


def _build_system_prompt(kb_text: str, user_platform: str | None = None) -> str:
    platform_context = ""
    if user_platform:
        platform_context = (
            f"\nThe user creates content on {user_platform}. "
            f"Personalize responses for {user_platform}-specific workflows."
        )

    return f"""You are Aria, a friendly sales assistant for AutoStream — an AI-powered video editing SaaS for content creators.

Personality: Warm, concise, enthusiastic. Like a knowledgeable friend, not a corporate bot.
{platform_context}

Knowledge base (use ONLY this for product info):
{kb_text}

Response style — THIS IS CRITICAL:
- Keep responses SHORT: 2-3 sentences for greetings, 3-5 for product info
- Use line breaks between distinct points
- Use bullet points with dashes (-) when listing features or benefits
- Do NOT use emojis in responses — keep it clean and professional
- Break info into scannable chunks, never write paragraph essays
- One thought per line

Rules:
- NEVER make up features or prices not in the knowledge base
- NEVER ask for personal info unless user shows buying interest
- NEVER ask for name, email, and platform in one message
- Celebrate warmly when a lead signs up

Internal task indicators (NEVER include these tags in your response):
- [COLLECT: name] — ask only for the user's name
- [COLLECT: email] — ask only for their email
- [COLLECT: platform] — ask only for their main content platform
- [LEAD_CAPTURED] — congratulate them warmly and offer next steps
- [INVALID_EMAIL] — the email was invalid, ask for a correct one
- [INVALID_NAME] — the name had numbers or special characters, ask for a valid name

CRITICAL: Never output [COLLECT: ...], [LEAD_CAPTURED], [INVALID_EMAIL], or [INVALID_NAME] in your response. These are internal system tags only."""


def _invoke_llm(system_prompt: str, messages: list[dict]) -> str:
    llm = _get_llm()
    langchain_messages = [SystemMessage(content=system_prompt)]

    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    response = llm.invoke(langchain_messages)
    return response.content


def router_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]["content"]
    intent = classify_intent(last_message, state)

    # ── LATENCY FIX: skip expensive RAG embedding for non-product queries ──
    needs_rag = intent in (Intent.PRODUCT_INQUIRY, Intent.HIGH_INTENT_LEAD, Intent.UNKNOWN)
    if needs_rag:
        rag_context = retrieve_context(last_message)
    else:
        rag_context = state.get("rag_context", "")

    detected_platform = _detect_platform_in_text(last_message)
    user_platform = state.get("user_platform") or detected_platform

    lead_score = calculate_lead_score({**state, "intent": intent})
    last_topic = detect_topic(last_message, intent)

    return {
        **state,
        "intent": intent,
        "rag_context": rag_context,
        "user_platform": user_platform,
        "lead_score": lead_score,
        "last_topic": last_topic,
    }


def product_qa_node(state: AgentState) -> AgentState:
    kb_text = _get_kb_text()
    system_prompt = _build_system_prompt(kb_text, state.get("user_platform"))
    reply = _invoke_llm(system_prompt, state["messages"])
    updated_messages = state["messages"] + [{"role": "assistant", "content": reply}]

    return {**state, "messages": updated_messages}


def lead_qualifier_node(state: AgentState) -> AgentState:
    kb_text = _get_kb_text()
    system_prompt = _build_system_prompt(kb_text, state.get("user_platform"))

    augmented = state["messages"] + [{
        "role": "user",
        "content": (
            "[COLLECT: name] The user has shown high intent to subscribe. "
            "Acknowledge their interest enthusiastically in 1-2 short lines, then ask ONLY for their name."
        ),
    }]

    reply = _invoke_llm(system_prompt, augmented)
    updated_messages = state["messages"] + [{"role": "assistant", "content": reply}]

    return {
        **state,
        "messages": updated_messages,
        "collecting_lead_info": True,
        "lead_score": 85,
    }


def lead_collector_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]["content"]
    extracted = extract_lead_info(last_message)

    lead_name = state.get("lead_name") or extracted.get("name")
    lead_email = state.get("lead_email") or extracted.get("email")
    lead_platform = state.get("lead_platform") or extracted.get("platform")

    # Fallback: treat short messages as a name (if we're collecting and don't have one yet)
    if not lead_name and not state.get("lead_name"):
        stripped = last_message.strip()
        if len(stripped.split()) <= 4 and "@" not in stripped:
            lead_name = stripped.title()

    # ── Name validation ──
    if lead_name and not state.get("lead_name") and not validate_name(lead_name):
        kb_text = _get_kb_text()
        system_prompt = _build_system_prompt(kb_text, state.get("user_platform"))
        augmented = state["messages"] + [{
            "role": "user",
            "content": "[INVALID_NAME] The name provided contains numbers or special characters. Politely ask for a valid name (letters only) in one short sentence.",
        }]
        reply = _invoke_llm(system_prompt, augmented)
        updated_messages = state["messages"] + [{"role": "assistant", "content": reply}]
        return {**state, "messages": updated_messages}

    # ── Email validation ──
    if lead_email and not validate_email(lead_email):
        kb_text = _get_kb_text()
        system_prompt = _build_system_prompt(kb_text, state.get("user_platform"))
        augmented = state["messages"] + [{
            "role": "user",
            "content": "[INVALID_EMAIL] The email provided appears invalid. Politely ask them to provide a valid email address in one short sentence.",
        }]
        reply = _invoke_llm(system_prompt, augmented)
        updated_messages = state["messages"] + [{"role": "assistant", "content": reply}]
        return {**state, "messages": updated_messages}

    # Auto-fill platform from earlier detection
    if not lead_platform and state.get("user_platform"):
        lead_platform = state["user_platform"]

    kb_text = _get_kb_text()
    system_prompt = _build_system_prompt(kb_text, state.get("user_platform"))

    if not lead_name:
        directive = "[COLLECT: name] Ask the user for their name in one friendly sentence."
    elif not lead_email:
        directive = f"[COLLECT: email] Thank {lead_name} briefly. Ask for their email in one sentence."
    elif not lead_platform:
        directive = "[COLLECT: platform] Ask which content platform they mainly use (YouTube, Instagram, TikTok, etc.) in one sentence."
    else:
        result = mock_lead_capture(lead_name, lead_email, lead_platform)
        directive = (
            f"[LEAD_CAPTURED] Lead ID: {result.get('lead_id', 'N/A')}. "
            f"Write a short, celebratory message (3-4 lines max) for {lead_name}. "
            f"No emojis. Mention the team will reach out to {lead_email} within 24 hours. "
            f"Reference their {lead_platform} content."
        )

    augmented = state["messages"] + [{"role": "user", "content": directive}]
    reply = _invoke_llm(system_prompt, augmented)
    updated_messages = state["messages"] + [{"role": "assistant", "content": reply}]

    all_captured = bool(lead_name and lead_email and lead_platform)

    return {
        **state,
        "messages": updated_messages,
        "lead_name": lead_name,
        "lead_email": lead_email,
        "lead_platform": lead_platform,
        "collecting_lead_info": not all_captured,
        "lead_captured": all_captured,
        "lead_score": 100 if all_captured else max(state.get("lead_score", 60), 75),
    }


def _route_after_router(state: AgentState) -> Literal["product_qa", "lead_qualifier", "lead_collector"]:
    intent = state.get("intent", Intent.UNKNOWN)
    collecting = state.get("collecting_lead_info", False)
    captured = state.get("lead_captured", False)

    if captured:
        return "product_qa"

    if collecting or intent == Intent.LEAD_INFO_RESPONSE:
        return "lead_collector"

    if intent == Intent.HIGH_INTENT_LEAD:
        return "lead_qualifier"

    return "product_qa"


def build_graph():
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("product_qa", product_qa_node)
    workflow.add_node("lead_qualifier", lead_qualifier_node)
    workflow.add_node("lead_collector", lead_collector_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "product_qa": "product_qa",
            "lead_qualifier": "lead_qualifier",
            "lead_collector": "lead_collector",
        },
    )

    workflow.add_edge("product_qa", END)
    workflow.add_edge("lead_qualifier", END)
    workflow.add_edge("lead_collector", END)

    return workflow.compile()


def get_initial_state() -> AgentState:
    return {
        "messages": [],
        "intent": Intent.UNKNOWN,
        "lead_score": 0,
        "collecting_lead_info": False,
        "lead_name": None,
        "lead_email": None,
        "lead_platform": None,
        "lead_captured": False,
        "rag_context": "",
        "user_platform": None,
        "last_topic": None,
    }
