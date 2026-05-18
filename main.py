"""
main.py
───────
Entry point for the WSP Engineering Intelligence Agent.

HOW TO RUN:
  1. Copy .env.example → .env and fill in your Azure credentials
  2. pip install -r requirements.txt
  3. python main.py

  For custom query:
  python main.py --query "What foundation type is suitable for a 5-storey
                           office building on soft clay in London?"

WHAT HAPPENS WHEN YOU RUN THIS:
  1. Loads environment variables (Azure OpenAI credentials)
  2. Builds the LangGraph agent graph
  3. Sends the query as a HumanMessage
  4. The agent loop runs:
       agent → decides to call tools → tools execute → agent reads results
       → agent decides to call more tools → ... → agent produces final answer
  5. Final report is printed and saved to output/

INTERVIEW TALKING POINT:
  "The agent autonomously decides the order and combination of tools to
   call. I don't hardcode a workflow — the LLM reasons about what
   information it needs, retrieves it, performs calculations, assesses
   risk, then writes the report. That's the core value of agentic AI
   over a simple chain: adaptive, multi-step reasoning."
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# ── Load credentials from .env before any Azure imports ──────────────────
load_dotenv()

# ── Validate credentials are present ─────────────────────────────────────
REQUIRED_ENV_VARS = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
]

def check_credentials() -> bool:
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        print("\n❌  Missing credentials in .env file:")
        for v in missing:
            print(f"    • {v}")
        print("\n    Copy .env.example → .env and fill in your Azure OpenAI credentials.")
        print("    See README.md → Setup section for detailed instructions.\n")
        return False
    return True

# ── Import agent (after env vars loaded) ─────────────────────────────────
from agent.graph import build_graph


# ═══════════════════════════════════════════════════════════════════════════
# DEMO QUERIES
# These showcase the agent's different capabilities.
# Each one exercises a different combination of tools.
# ═══════════════════════════════════════════════════════════════════════════

DEMO_QUERIES = {
    "1": (
        "Foundation design on soft clay",
        """I am designing foundations for a new 5-storey office building
        (150 kN/m dead load, 75 kN/m live load) on a site in London
        with soft clay soils. Undrained shear strength Cu = 35 kPa.
        What foundation type do you recommend, what are the key design
        considerations per Eurocode 7, and what are the main risks?
        Provide a structured engineering report."""
    ),
    "2": (
        "Pedestrian footbridge load assessment",
        """We are designing a 30m span pedestrian footbridge over a canal
        in Manchester. Dead load = 8 kN/m², live load = 5 kN/m², wind = 2 kN/m².
        Calculate the design ULS load combination per Eurocode EN 1990,
        assess the key structural risks, and produce an engineering report."""
    ),
    "3": (
        "Urban tunnel environmental and safety assessment",
        """We are proposing a 1.2km TBM tunnel beneath central Birmingham
        passing within 15m of a Victorian Grade II listed viaduct.
        Ground conditions: London clay, Cu = 60 kPa. What are the
        environmental, structural, and safety risks? What monitoring
        is required? Produce a risk-focused engineering report."""
    ),
    "4": (
        "Net zero carbon assessment for infrastructure project",
        """Estimate the embodied carbon for a new infrastructure project:
        500 m³ concrete, 45 tonnes structural steel, 120 m³ engineered
        timber, transport 8,000 tonne-km. Assess against RICS benchmarks,
        identify reduction strategies, and produce a sustainability report."""
    ),
}


def run_agent(query: str, project_name: str = "Engineering Assessment") -> str:
    """
    Run the LangGraph agent on a query and return the final answer.

    Args:
        query:        The engineering question to answer
        project_name: Label for the output report

    Returns:
        The agent's final response string
    """
    print("\n" + "═"*62)
    print("  WSP ENGINEERING INTELLIGENCE AGENT")
    print("  Powered by Azure OpenAI + LangGraph")
    print("═"*62)
    print(f"\n  PROJECT: {project_name}")
    print(f"\n  QUERY:\n  {query[:200]}{'...' if len(query) > 200 else ''}")
    print("\n" + "─"*62)

    # Build and run the graph
    app = build_graph()

    # Stream the execution (shows tool calls in real time)
    final_answer = ""
    step_count   = 0

    for step in app.stream(
        {"messages": [HumanMessage(content=query)]},
        config={"recursion_limit": 25},  # Max tool call cycles
    ):
        step_count += 1

        # The step is a dict: {node_name: state}
        node_name = list(step.keys())[0]
        node_state = step[node_name]

        if node_name == "agent":
            last_msg = node_state["messages"][-1]
            if hasattr(last_msg, "content") and last_msg.content:
                # This is the final answer (no tool calls)
                if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                    final_answer = last_msg.content

    print(f"\n[Agent] ✓ Completed in {step_count} steps.")
    print("\n" + "═"*62)
    print("  AGENT RESPONSE")
    print("═"*62)
    print(final_answer)

    # Save to output file
    _save_output(project_name, query, final_answer)

    return final_answer


def _save_output(project_name: str, query: str, response: str):
    """Save the agent's response to a timestamped text file."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in project_name)[:40]
    filename = output_dir / f"{timestamp}_{safe_name}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"WSP Engineering Intelligence Agent — Output\n")
        f.write(f"{'='*60}\n")
        f.write(f"Project:   {project_name}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%d %B %Y %H:%M UTC')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"QUERY:\n{query}\n\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"RESPONSE:\n{response}\n")

    print(f"\n[Output] ✓ Saved to {filename}")


def interactive_mode():
    """Run the agent in interactive menu mode."""
    print("\n" + "═"*62)
    print("  WSP ENGINEERING INTELLIGENCE AGENT")
    print("  SELECT A DEMO OR ENTER YOUR OWN QUERY")
    print("═"*62)

    for key, (title, _) in DEMO_QUERIES.items():
        print(f"  [{key}] {title}")
    print("  [c] Enter custom query")
    print("  [q] Quit")
    print("─"*62)

    choice = input("\n  Your choice: ").strip().lower()

    if choice == "q":
        print("  Exiting. Good luck with the interview, Haroun! 🚀\n")
        sys.exit(0)
    elif choice == "c":
        project = input("  Project name: ").strip() or "Custom Assessment"
        query   = input("  Your query:\n  > ").strip()
        if query:
            run_agent(query, project)
    elif choice in DEMO_QUERIES:
        project, query = DEMO_QUERIES[choice]
        run_agent(query, project)
    else:
        print("  Invalid choice. Please try again.")
        interactive_mode()


# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WSP Engineering Intelligence Agent"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Engineering query to process directly (skips interactive menu)"
    )
    parser.add_argument(
        "--project", "-p",
        type=str,
        default="Engineering Assessment",
        help="Project name for the output report"
    )
    parser.add_argument(
        "--demo", "-d",
        type=str,
        choices=list(DEMO_QUERIES.keys()),
        help="Run a specific demo query (1-4)"
    )

    args = parser.parse_args()

    # ── Check credentials first ───────────────────────────────────────
    if not check_credentials():
        sys.exit(1)

    # ── Route to appropriate mode ─────────────────────────────────────
    if args.demo:
        project, query = DEMO_QUERIES[args.demo]
        run_agent(query, project)
    elif args.query:
        run_agent(args.query, args.project)
    else:
        interactive_mode()
