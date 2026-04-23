# AutoStream AI Sales Agent

AutoStream AI is a production-grade conversational sales agent built to automate lead generation and handle customer inquiries. Powered by large language models and vector database retrieval, the agent autonomously answers product questions, detects high-intent users, and seamlessly transitions into a lead capture workflow. 

It features a high-performance Streamlit dashboard for web interactions and includes a complete FastAPI backend infrastructure for deployment to the Meta WhatsApp Business API.

---

## Technical Stack

*   **Core Logic:** Python 3.9+
*   **Orchestration:** LangGraph (StateGraph for deterministic multi-turn conversations)
*   **Chat Model:** Llama 3.3 70B Versatile (via Groq)
*   **Intent Classification:** Llama 3.1 8B Instant (via Groq)
*   **Retrieval-Augmented Generation (RAG):** FAISS Vector Store
*   **Embeddings:** Google text-embedding-004
*   **Web Dashboard:** Streamlit (with custom premium CSS architecture)
*   **WhatsApp Backend:** FastAPI, Uvicorn, Requests

---

## Capabilities and Supported Queries

The agent is designed to handle a wide range of customer interactions dynamically:

### 1. General Product Inquiries
The agent uses RAG to pull accurate information from the internal knowledge base.
*   "What are the differences between the Basic and Pro plans?"
*   "Do you offer a free trial?"
*   "What is your refund policy?"

### 2. Intent Detection and Lead Scoring
The system continuously analyzes user input to calculate a "Lead Score" (Low, Medium, or High). When a user exhibits buying intent, the agent automatically pivots from answering questions to collecting lead information.

### 3. Sequential Lead Capture
Upon detecting high intent, the agent initiates a strict data collection workflow:
*   Collects and validates the user's name (alphabetic characters only).
*   Collects and validates the user's email address (format verification and disposable domain blocking).
*   Detects or explicitly asks for the user's primary content platform.
*   Executes the `mock_lead_capture` backend function only when all constraints are met.

---

## Local Setup and Installation

Follow these instructions to run the web dashboard and the WhatsApp backend locally.

### Prerequisites
*   Python 3.9 or higher
*   Groq API Key
*   Google AI Studio API Key

### Step 1: Clone and Configure Environment
1. Clone the repository and navigate to the project directory.
2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```
3. Install all required dependencies:
```bash
pip install -r requirements.txt
```
4. Copy the environment template and add your API keys:
```bash
cp .env.example .env
```
Open `.env` and configure `GROQ_API_KEY` and `GOOGLE_API_KEY`.

### Step 2: Run the Web Dashboard
To launch the visual Streamlit interface:
```bash
streamlit run streamlit_app.py
```
The application will be accessible at `http://localhost:8501`.

---

## WhatsApp Integration Setup

The repository includes a complete FastAPI backend (`whatsapp_server.py`) designed to interface with the Meta WhatsApp Business Cloud API via webhooks. The backend utilizes the exact same LangGraph logic as the web dashboard and features an in-memory session manager to track conversations across different phone numbers.

### Running the Backend Server
In a separate terminal window (with the virtual environment activated), start the server:
```bash
uvicorn whatsapp_server:app --reload --port 8000
```
The webhook endpoint will be active at `http://localhost:8000/webhook`.

### Connecting to Meta
To deploy this integration to a live WhatsApp number:
1.  Configure the `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, and `WEBHOOK_VERIFY_TOKEN` variables in your `.env` file.
2.  Expose your local server to the internet using a secure tunnel service like ngrok:
```bash
ngrok http 8000
```
3.  Navigate to the Meta Developer Dashboard for your application.
4.  Set up the WhatsApp product and enter your ngrok URL (e.g., `https://your-url.ngrok-free.app/webhook`) as the webhook destination.
5.  Provide the custom verify token you defined in your `.env` file to complete the handshake.

The agent will now receive messages from WhatsApp, process them through the LangGraph state machine, and automatically reply to the user.
