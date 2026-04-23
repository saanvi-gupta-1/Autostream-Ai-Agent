# AutoStream AI Sales Agent — Aria

> **Social-to-Lead Agentic Workflow** | ServiceHive x Inflx ML Internship Assignment

A production-grade conversational AI agent that handles product queries, detects high-intent users, and captures qualified leads — powered by **Llama 3.3 70B (Groq)**, **LangGraph**, **FAISS vector search**, and a **Streamlit chat interface**.

---

## Table of Contents

1. [Demo](#demo)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [How to Run Locally](#how-to-run-locally)
5. [Architecture Explanation](#architecture-explanation)
6. [Conversation Flow](#conversation-flow)
7. [WhatsApp Deployment via Webhooks](#whatsapp-deployment-via-webhooks)
8. [Evaluation Checklist](#evaluation-checklist)

---

## Demo

> Watch the 2-3 minute screen recording in `demo/demo_video.mp4`

The demo covers:
1. Agent answering a pricing question using RAG retrieval
2. Agent detecting high-intent and shifting to lead qualification
3. Sequential collection of name, email, and platform
4. Successful `mock_lead_capture()` execution with confirmation banner

---

## Features

| Capability | Implementation |
|---|---|
| **Intent Detection** | LLM-based classification (Llama 3.1 8B via Groq) with regex fallback |
| **RAG Pipeline** | FAISS vector store + Google `text-embedding-004` embeddings |
| **Multi-turn Memory** | LangGraph `AgentState` TypedDict persisted across turns |
| **Lead Scoring** | Three-tier scoring system (Low / Medium / High) |
| **Lead Collection** | Sequential one-field-at-a-time conversational flow |
| **Email Validation** | Regex validation before lead capture execution |
| **Tool Execution** | `mock_lead_capture()` triggered only when all 3 fields are valid |
| **Platform Personalization** | Responses tailored to user's content platform |
| **Streamlit UI** | Chat bubbles, live sidebar state, lead capture banner |
| **CLI Interface** | Terminal-based chat with state inspection |

---

## Project Structure

```
autostream-agent/
|
|-- app.py                     # CLI entry point
|-- streamlit_app.py           # Streamlit chat interface
|-- agent_logic.py             # LangGraph StateGraph, nodes, routing
|-- intent.py                  # LLM + regex intent classification, lead scoring
|-- rag_pipeline.py            # FAISS vector store, embeddings, retrieval
|-- tools.py                   # mock_lead_capture(), email validation
|
|-- knowledge_base/
|   +-- autostream_kb.json     # Product pricing, policies, FAQ
|
|-- requirements.txt
|-- .env.example
+-- README.md
```

---

## How to Run Locally

### Prerequisites

- Python 3.9+
- A [Groq API Key](https://console.groq.com/keys) (free tier available)
- A [Google AI Studio API Key](https://aistudio.google.com/apikey) (for embeddings)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure API Keys

```bash
cp .env.example .env
```

Open `.env` and add your keys:

```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 5 — Run the Agent

**Option A: Streamlit UI (Recommended)**

```bash
streamlit run streamlit_app.py
```

This opens a browser-based chat interface at `http://localhost:8501`.

**Option B: CLI Mode**

```bash
python app.py
```

### Debug Commands (CLI only)

| Command | Description |
|---|---|
| `state` | Inspect current lead state and scoring |
| `exit` / `quit` | End the session |

---

## Architecture Explanation

### Why LangGraph?

LangGraph was chosen over AutoGen because it provides **explicit, inspectable state management** via a typed `AgentState` dictionary. Every conversation turn — message history, intent classification, lead fields, scoring, and collection flags — lives in a single state object that flows through all graph nodes deterministically. This makes the agent fully debuggable and prevents premature tool execution, which is critical for a lead-capture workflow.

### How State is Managed

The graph follows a **router-to-worker** architecture:

1. **Router Node** — Classifies intent using a dedicated Llama 3.1 8B call via Groq (with regex fallback), retrieves relevant context from the FAISS vector store via similarity search, detects the user's platform, and computes a lead score.
2. **Conditional Edge** — Routes to `product_qa`, `lead_qualifier`, or `lead_collector` based on intent classification and current state flags.
3. **Worker Nodes** — Each node updates state fields (messages, lead info, collection flags) and invokes Llama 3.3 70B via Groq with the full message history plus system directives.
4. **Tool Execution** — `mock_lead_capture()` fires inside `lead_collector_node` only when all three fields (name, email, platform) are validated. Email format is checked before capture.

The **full message history** persists in `AgentState.messages`, giving the LLM complete context across 5-6+ turns without external memory stores. The RAG pipeline uses Google `text-embedding-004` embeddings with FAISS similarity search to retrieve the most relevant knowledge base chunks per query, falling back to keyword matching if the embedding API is unavailable.

---

## Conversation Flow

```
User: "Hi, tell me about your pricing."
  |-- Intent: PRODUCT_INQUIRY (LLM classified via Groq)
  |-- FAISS retrieves pricing documents from vector store
  +-- Aria explains Basic ($29/mo) and Pro ($79/mo) plans

User: "That sounds great, I want to try the Pro plan for my YouTube channel."
  |-- Intent: HIGH_INTENT_LEAD
  |-- Platform detected: YouTube (remembered for session)
  |-- Routes to lead_qualifier_node
  +-- Aria: "Awesome! I'd love to get you set up. What's your name?"

User: "Rahul Sharma"
  |-- Intent: LEAD_INFO_RESPONSE (collecting_lead_info=True)
  |-- lead_name = "Rahul Sharma"
  +-- Aria: "Great to meet you, Rahul! What's your email address?"

User: "rahul@example.com"
  |-- Email validated via regex
  |-- lead_email = "rahul@example.com"
  |-- lead_platform auto-filled = "Youtube" (from earlier detection)
  |-- mock_lead_capture("Rahul Sharma", "rahul@example.com", "Youtube") called
  +-- Aria: "You're all set, Rahul! Our team will reach out within 24 hours!"
```

---

## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, the **WhatsApp Business Cloud API** (Meta) with a webhook architecture would be used:

### Architecture

```
WhatsApp User
      |
      V (sends message)
WhatsApp Cloud API
      |
      V HTTP POST (webhook event)
Webhook Server  <-- FastAPI / Flask endpoint
      |
      |-- Validate X-Hub-Signature-256
      |-- Extract sender phone number + message text
      |-- Load session state from Redis (keyed by phone number)
      |-- Run LangGraph agent with graph.invoke(state)
      |-- Save updated state back to Redis
      +-- POST reply to WhatsApp Cloud API
            |
            V
      WhatsApp User receives response
```

### Implementation Steps

1. **Register a Meta Developer App** and enable the WhatsApp Business API with a verified business number.

2. **Create a Webhook Endpoint** using FastAPI:

```python
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    phone = message["from"]
    text = message["text"]["body"]

    state = redis_client.get(f"session:{phone}") or get_initial_state()

    state["messages"].append({"role": "user", "content": text})
    updated_state = graph.invoke(state)

    redis_client.set(f"session:{phone}", json.dumps(updated_state), ex=3600)

    reply = updated_state["messages"][-1]["content"]
    send_whatsapp_message(phone, reply)

    return {"status": "ok"}
```

3. **Persist Per-User State** using Redis keyed by phone number for isolated multi-turn memory with automatic session expiry.

4. **Deploy** on a cloud platform (AWS Lambda, Railway, or Render) with HTTPS for Meta webhook verification.

---

## Evaluation Checklist

| Criterion | Status | Location |
|---|---|---|
| Intent Detection (LLM + fallback) | Done | `intent.py` |
| RAG with Embeddings + FAISS | Done | `rag_pipeline.py` |
| Tool Execution (lead capture) | Done | `tools.py` |
| State Management (5-6 turns) | Done | `agent_logic.py` — LangGraph `AgentState` |
| Lead Scoring (3 tiers) | Done | `intent.py` — `calculate_lead_score()` |
| Platform Personalization | Done | `agent_logic.py` — `_build_system_prompt()` |
| Email Validation | Done | `tools.py` — `validate_email()` |
| Streamlit UI | Done | `streamlit_app.py` |
| CLI Interface | Done | `app.py` |
| requirements.txt | Done | Project root |
| README with Architecture | Done | This file |
| WhatsApp Webhook Explanation | Done | Section above |
| Demo Video | Done | `demo/demo_video.mp4` |

---

## Tech Stack

| Component | Technology |
|---|---|
| **LLM (Chat)** | Llama 3.3 70B Versatile via Groq |
| **LLM (Intent)** | Llama 3.1 8B Instant via Groq |
| **Framework** | LangGraph `StateGraph` with typed state |
| **Embeddings** | Google `text-embedding-004` |
| **Vector Store** | FAISS (in-memory, built from local JSON KB) |
| **RAG Fallback** | Keyword-based retrieval |
| **UI** | Streamlit with custom CSS |
| **Memory** | Full message history in `AgentState.messages` |
| **Language** | Python 3.9+ |

---

*Built for the ServiceHive x Inflx ML Internship Assignment*
