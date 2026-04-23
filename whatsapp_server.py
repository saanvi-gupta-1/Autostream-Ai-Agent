import os
import json
import logging
from typing import Dict, Any
import requests
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

# Load agent logic
from agent_logic import build_graph, get_initial_state

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "")

app = FastAPI(title="AutoStream WhatsApp Webhook")

# ─── Session Management ───
# In-memory session store mapping phone numbers to their AgentState
# Note: For production, replace this with Redis or a database.
sessions: Dict[str, Any] = {}
graph = build_graph()

def get_session(phone_number: str) -> Any:
    """Retrieve or create a session for a user."""
    if phone_number not in sessions:
        logger.info(f"Creating new session for {phone_number}")
        sessions[phone_number] = get_initial_state()
    return sessions[phone_number]

def save_session(phone_number: str, state: Any):
    """Save the updated session state."""
    sessions[phone_number] = state


# ─── WhatsApp API Client ───
def send_whatsapp_message(to: str, text: str):
    """Send a text message back to the user via WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials missing. Message not sent.")
        return

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent to {to}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {e}")
        if response is not None:
            logger.error(f"Response: {response.text}")


# ─── Webhook Endpoints ───

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Meta requires a GET request to verify the webhook URL.
    It passes hub.mode, hub.verify_token, and hub.challenge.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully.")
            return Response(content=challenge, status_code=200)
        else:
            return Response(status_code=403)
    return Response(status_code=400)


@app.post("/webhook")
async def receive_message(request: Request):
    """
    Receive incoming messages from WhatsApp.
    """
    body = await request.json()
    
    # Check if this is a WhatsApp API event
    if body.get("object") == "whatsapp_business_account":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Check if there are messages
                if "messages" in value:
                    for message in value["messages"]:
                        # We only handle text messages in this demo
                        if message.get("type") == "text":
                            phone_number = message["from"]
                            text = message["text"]["body"]
                            
                            logger.info(f"Received message from {phone_number}: {text}")
                            
                            # 1. Load session
                            state = get_session(phone_number)
                            
                            # 2. Append user message
                            state["messages"].append({"role": "user", "content": text})
                            
                            # 3. Invoke LangGraph
                            try:
                                updated_state = graph.invoke(state)
                                save_session(phone_number, updated_state)
                                
                                # 4. Get AI reply
                                reply = updated_state["messages"][-1]["content"]
                                
                                # 5. Send reply back to WhatsApp
                                send_whatsapp_message(phone_number, reply)
                                
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                                send_whatsapp_message(
                                    phone_number, 
                                    "I'm sorry, I'm having a temporary issue processing your request."
                                )

    # Always return 200 OK to Meta to acknowledge receipt
    return Response(status_code=200)

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "AutoStream WhatsApp Webhook"}
