import os
import re
from enum import Enum
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


class Intent(str, Enum):
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    HIGH_INTENT_LEAD = "high_intent_lead"
    LEAD_INFO_RESPONSE = "lead_info_response"
    UNKNOWN = "unknown"


INTENT_DISPLAY_LABELS = {
    "greeting": "Greeting",
    "product_inquiry": "Inquiry",
    "high_intent_lead": "High Intent",
    "lead_info_response": "Lead Capture",
    "unknown": "New Session",
}


INTENT_SYSTEM_PROMPT = """Classify the user message into exactly one category.

Categories:
- GREETING: casual greetings like hi, hello, hey, good morning
- PRODUCT_INQUIRY: questions about pricing, features, plans, capabilities, comparisons, policies, refunds, support
- HIGH_INTENT_LEAD: user wants to sign up, try, subscribe, buy, purchase, get started, is ready to commit

Respond with ONLY the category name in uppercase. Nothing else."""


GREETING_PATTERNS = [
    r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bgood (morning|afternoon|evening)\b",
    r"\bwhat'?s up\b", r"\bgreetings\b", r"\bhowdy\b", r"\byo\b",
]

HIGH_INTENT_PATTERNS = [
    r"\bi('?m| am) (interested|ready|want|looking)\b",
    r"\bsign me up\b",
    r"\bi want to (try|start|subscribe|get|buy|purchase|use)\b",
    r"\blet'?s (do|go|start|get)\b",
    r"\bi('?ll| will) (take|go with|try|subscribe|choose)\b",
    r"\bwhere do i sign\b",
    r"\bhow do i sign up\b",
    r"\bcan i (start|try|get|subscribe|sign up)\b",
    r"\bready to\b",
    r"\bsign up\b",
    r"\bget started\b",
    r"\btry (the )?(pro|basic) plan\b",
    r"\bpurchase\b",
    r"\bsubscribe\b",
    r"\bcount me in\b",
    r"\bi('?d| would) like to (join|start|try|sign|get)\b",
    r"\byes\b",
    r"\byeah\b",
    r"\byep\b",
    r"\bsure\b",
    r"\bokay\b",
    r"\bok\b",
    r"\bokie\b",
]

EMAIL_PATTERN = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"

# Use word-boundary matching to avoid "x" matching inside "example"
PLATFORMS = {
    "youtube": "YouTube",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "twitter": "Twitter",
    "linkedin": "LinkedIn",
    "twitch": "Twitch",
    "snapchat": "Snapchat",
    "pinterest": "Pinterest",
}
# "x" needs special handling — only match standalone "x" or "x.com"
X_PATTERN = r"(?:\bx\.com\b|\bon x\b|\bfor x\b|\buse x\b|\bmy x\b)"


def _classify_with_llm(message: str) -> Intent | None:
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=10,
        )
        response = llm.invoke([
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=message),
        ])
        result = response.content.strip().upper().replace(" ", "_")
        mapping = {
            "GREETING": Intent.GREETING,
            "PRODUCT_INQUIRY": Intent.PRODUCT_INQUIRY,
            "HIGH_INTENT_LEAD": Intent.HIGH_INTENT_LEAD,
        }
        return mapping.get(result)
    except Exception:
        return None


def _classify_with_rules(message: str) -> Intent:
    msg = message.lower().strip()

    for pattern in HIGH_INTENT_PATTERNS:
        if re.search(pattern, msg):
            return Intent.HIGH_INTENT_LEAD

    for pattern in GREETING_PATTERNS:
        if re.search(pattern, msg):
            if len(msg.split()) <= 5:
                return Intent.GREETING

    return Intent.PRODUCT_INQUIRY


def classify_intent(message: str, state: dict) -> Intent:
    if state.get("collecting_lead_info", False):
        return Intent.LEAD_INFO_RESPONSE

    if re.search(EMAIL_PATTERN, message):
        return Intent.LEAD_INFO_RESPONSE

    # For short messages (1-3 words), rules are faster + accurate enough
    if len(message.split()) <= 3:
        return _classify_with_rules(message)

    llm_result = _classify_with_llm(message)
    if llm_result is not None:
        return llm_result

    return _classify_with_rules(message)


def _detect_platform_in_text(text: str) -> str | None:
    """Detect platform using word-boundary matching to avoid false positives."""
    text_lower = text.lower()

    # Check named platforms first (safe word-boundary match)
    for key, display in PLATFORMS.items():
        if re.search(rf"\b{key}\b", text_lower):
            return display

    # Special handling for "X" — requires specific context
    if re.search(X_PATTERN, text_lower):
        return "X (Twitter)"

    return None


def extract_lead_info(message: str) -> dict:
    extracted = {}

    email_match = re.search(EMAIL_PATTERN, message)
    if email_match:
        extracted["email"] = email_match.group(0).lower()

    platform = _detect_platform_in_text(message)
    if platform:
        extracted["platform"] = platform

    name_patterns = [
        r"(?:my name is|i'?m|i am|call me|name'?s)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            platform_names = [v.lower() for v in PLATFORMS.values()]
            if "@" not in candidate and candidate.lower() not in platform_names:
                extracted["name"] = candidate.title()
            break

    return extracted


def calculate_lead_score(state: dict) -> int:
    points = 0

    intent = state.get("intent", "")
    if intent == Intent.HIGH_INTENT_LEAD:
        points += 55
    elif intent == Intent.PRODUCT_INQUIRY:
        points += 35
    elif intent == Intent.GREETING:
        points += 10
    else:
        points += 5

    messages = state.get("messages", [])
    user_msgs = [m for m in messages if m.get("role") == "user"]
    points += min(12, len(user_msgs) * 3)

    msg_text = " ".join([m.get("content", "").lower() for m in messages if m.get("role") == "user"])
    feature_kw = ["feature", "4k", "caption", "export", "compare", "difference", "mobile", "team", "resolution"]
    if any(kw in msg_text for kw in feature_kw):
        points += 8

    if state.get("collecting_lead_info") or state.get("lead_name"):
        points += 8
    if state.get("lead_email"):
        points += 8
    if state.get("lead_platform") or state.get("user_platform"):
        points += 5

    if state.get("lead_captured"):
        return 100

    return min(99, max(5, points))


def get_score_label(score: int) -> str:
    if score >= 75:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"


def detect_topic(message: str, intent: str) -> str:
    msg = message.lower()

    if intent == Intent.HIGH_INTENT_LEAD:
        return "Subscription"
    if intent == Intent.LEAD_INFO_RESPONSE:
        return "Lead Qualification"

    if any(kw in msg for kw in ["price", "pricing", "cost", "plan", "how much", "pay"]):
        return "Pricing"
    if any(kw in msg for kw in ["feature", "what can", "capability", "do you offer", "4k", "caption"]):
        return "Features"
    if any(kw in msg for kw in ["refund", "cancel", "policy", "return"]):
        return "Policies"
    if any(kw in msg for kw in ["support", "help", "contact"]):
        return "Support"
    if any(kw in msg for kw in ["trial", "free", "demo"]):
        return "Free Trial"
    if intent == Intent.GREETING:
        return "General"

    return "Product Info"
