import os
import json
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

KB_PATH = Path(__file__).parent / "knowledge_base" / "autostream_kb.json"

_vectorstore = None
_kb_cache = None


def _load_knowledge_base() -> dict:
    global _kb_cache
    if _kb_cache is None:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            _kb_cache = json.load(f)
    return _kb_cache


def _build_documents() -> list[Document]:
    kb = _load_knowledge_base()
    docs = []

    company = kb["company"]
    docs.append(Document(
        page_content=(
            f"Company Overview: {company['name']} - {company['tagline']}. "
            f"{company['description']}"
        ),
        metadata={"section": "overview"},
    ))

    for plan in kb["plans"]:
        features = ", ".join(plan["features"])
        docs.append(Document(
            page_content=(
                f"{plan['name']} - ${plan['price_monthly']}/month "
                f"(${plan['price_annual']}/year). "
                f"Best for: {plan['best_for']}. "
                f"Features: {features}."
            ),
            metadata={"section": "pricing", "plan": plan["name"]},
        ))

    for policy in kb["policies"]:
        docs.append(Document(
            page_content=f"{policy['topic']}: {policy['details']}",
            metadata={"section": "policy", "topic": policy["topic"]},
        ))

    for faq in kb["faq"]:
        docs.append(Document(
            page_content=f"Q: {faq['question']} A: {faq['answer']}",
            metadata={"section": "faq"},
        ))

    return docs


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


def build_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    docs = _build_documents()
    embeddings = _get_embeddings()
    _vectorstore = FAISS.from_documents(docs, embeddings)
    return _vectorstore


def retrieve_context(query: str, k: int = 2) -> str:
    try:
        vs = build_vectorstore()
        results = vs.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception:
        return _keyword_fallback(query)


def _keyword_fallback(query: str) -> str:
    kb = _load_knowledge_base()
    query_lower = query.lower()
    parts = []

    parts.append(f"{kb['company']['name']}: {kb['company']['description']}")

    price_kw = [
        "price", "pricing", "cost", "plan", "basic", "pro", "month",
        "pay", "subscription", "how much", "upgrade", "4k", "unlimited",
        "features", "difference", "compare",
    ]
    if any(kw in query_lower for kw in price_kw):
        for plan in kb["plans"]:
            features = ", ".join(plan["features"])
            parts.append(
                f"{plan['name']}: ${plan['price_monthly']}/month. "
                f"Features: {features}. Best for: {plan['best_for']}."
            )

    policy_kw = [
        "refund", "cancel", "support", "help", "policy", "return",
        "trial", "free", "7 day", "24/7", "platform",
    ]
    if any(kw in query_lower for kw in policy_kw):
        for p in kb["policies"]:
            parts.append(f"{p['topic']}: {p['details']}")

    faq_kw = ["team", "enterprise", "mobile", "caption", "how does", "can i"]
    if any(kw in query_lower for kw in faq_kw):
        for f in kb["faq"]:
            parts.append(f"Q: {f['question']} A: {f['answer']}")

    if len(parts) == 1:
        for plan in kb["plans"]:
            features = ", ".join(plan["features"])
            parts.append(f"{plan['name']}: ${plan['price_monthly']}/month. Features: {features}.")
        for p in kb["policies"]:
            parts.append(f"{p['topic']}: {p['details']}")

    return "\n\n".join(parts)


def get_full_knowledge_base_text() -> str:
    kb = _load_knowledge_base()
    parts = []

    parts.append(f"{kb['company']['name']}: {kb['company']['description']}")

    for plan in kb["plans"]:
        features = "\n  - ".join(plan["features"])
        parts.append(
            f"{plan['name']} - ${plan['price_monthly']}/month "
            f"(${plan['price_annual']}/year)\n"
            f"Best for: {plan['best_for']}\n"
            f"Features:\n  - {features}"
        )

    for p in kb["policies"]:
        parts.append(f"{p['topic']}: {p['details']}")

    for f in kb["faq"]:
        parts.append(f"Q: {f['question']}\nA: {f['answer']}")

    return "\n\n".join(parts)
