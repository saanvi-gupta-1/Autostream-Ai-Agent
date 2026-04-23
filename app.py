import os
import sys
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def validate_environment():
    if not os.getenv("GROQ_API_KEY"):
        print("\n  [X] GROQ_API_KEY not found.")
        print("      Create a .env file with: GROQ_API_KEY=your_key_here\n")
        sys.exit(1)


def display_banner():
    print()
    print("=" * 62)
    print("   AutoStream AI Sales Assistant - Aria")
    print("   Powered by Llama 3.3 70B (Groq) + LangGraph + FAISS RAG")
    print("=" * 62)
    print("   Type your message and press Enter to chat.")
    print("   Type 'quit' or 'exit' to end the session.")
    print("   Type 'state' to inspect current agent state.")
    print("=" * 62)
    print()


def display_lead_state(state: dict):
    from intent import get_score_label, INTENT_DISPLAY_LABELS

    score = state.get("lead_score", 0)
    label = get_score_label(score)
    intent_raw = state.get("intent", "unknown")
    intent_label = INTENT_DISPLAY_LABELS.get(intent_raw, intent_raw)
    topic = state.get("last_topic", "--")
    status = "Captured" if state.get("lead_captured") else "Active"

    bar_filled = int(score / 5)
    bar = "#" * bar_filled + "-" * (20 - bar_filled)

    print()
    print("+--------------------------------------+")
    print("|         Current Lead State           |")
    print("+--------------------------------------+")
    print(f"|  Intent:     {intent_label:>22} |")
    print(f"|  Score:      {f'{score}% ({label})':>22} |")
    print(f"|  Progress:   [{bar}] |")
    print(f"|  Topic:      {topic:>22} |")
    print("+--------------------------------------+")
    print(f"|  Name:       {(state.get('lead_name') or 'Waiting'):>22} |")
    print(f"|  Email:      {(state.get('lead_email') or 'Waiting'):>22} |")
    print(f"|  Platform:   {(state.get('lead_platform') or state.get('user_platform') or 'Waiting'):>22} |")
    print(f"|  Status:     {status:>22} |")
    print("+--------------------------------------+")
    print()


def run():
    from agent_logic import build_graph, get_initial_state

    graph = build_graph()
    state = get_initial_state()

    print("Aria: Hey there! I'm Aria, AutoStream's AI assistant.")
    print("      Ask me about plans, pricing, or get started with a free trial!")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nAria: Thanks for chatting! Have a great day!\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print("\nAria: Thanks for stopping by! Can't wait to have you on AutoStream.\n")
            break

        if user_input.lower() == "state":
            display_lead_state(state)
            continue

        state["messages"].append({"role": "user", "content": user_input})

        try:
            result = graph.invoke(state)
            state = result
            last_reply = state["messages"][-1]["content"]
            print(f"\nAria: {last_reply}\n")
        except Exception as e:
            print(f"\n  [!] Error: {e}")
            print("      Please check your API key and try again.\n")


def main():
    validate_environment()
    display_banner()
    run()


if __name__ == "__main__":
    main()
