"""
graph.py
────────
THE HEART OF THE AGENTIC SYSTEM — The LangGraph StateGraph.

WHAT IS A LANGGRAPH GRAPH?
  A graph is a set of NODES connected by EDGES.
  - Nodes  = units of work (LLM call, tool execution, logic)
  - Edges  = transitions between nodes (fixed or conditional)
  - State  = a shared dict that flows through every node and
             accumulates the full conversation + tool results

THE AGENT LOOP (ReAct pattern):
  ┌──────────────────────────────────────────────┐
  │                                              │
  │   [agent_node] ──── has tool calls? ────►  [tool_node]
  │        ▲                                      │
  │        └──────────────────────────────────────┘
  │
  │   [agent_node] ──── no tool calls? ────► END
  │
  └──────────────────────────────────────────────┘

"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.azure_client import get_llm
from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    search_engineering_documents,
    calculate_engineering_metric,
    classify_risk_level,
    generate_structured_report,
)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: DEFINE STATE
# The state is the shared memory that flows through every node.
# add_messages is a reducer — it appends new messages rather than replacing.
# ═══════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: DEFINE THE TOOLS LIST
# These are the 4 tools the agent can choose from.
# ═══════════════════════════════════════════════════════════════════════════

TOOLS = [
    search_engineering_documents,
    calculate_engineering_metric,
    classify_risk_level,
    generate_structured_report,
]


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: BIND TOOLS TO THE LLM
# .bind_tools() injects the tool schemas into the LLM's context so it
# knows exactly what tools exist, what arguments they take, and when to
# call them. The LLM outputs structured tool_call JSON when it wants a tool.
# ═══════════════════════════════════════════════════════════════════════════

llm  = get_llm(temperature=0.1)
llm_with_tools = llm.bind_tools(TOOLS)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: DEFINE THE AGENT NODE
# This is the node that calls the LLM. It:
#   1. Prepends the system prompt on the first call
#   2. Passes the full message history to the LLM
#   3. Returns the LLM's response (which may contain tool_calls)
# ═══════════════════════════════════════════════════════════════════════════

def agent_node(state: AgentState) -> AgentState:
    """
    The agent node — calls Azure OpenAI with the full conversation history.

    On the first call, injects the system prompt as the first message.
    The LLM either:
      a) Returns a final answer (no tool_calls) → graph ends
      b) Returns tool_calls → ToolNode executes them → loop continues
    """
    messages = list(state["messages"])

    # Inject system prompt if this is the first turn
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    print("\n[Agent] Thinking...")
    response = llm_with_tools.invoke(messages)

    # Show which tools were called (for transparency / debugging)
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            print(f"[Agent] ► Calling tool: {tc['name']}")
            if tc.get("args"):
                for k, v in tc["args"].items():
                    preview = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
                    print(f"         {k}: {preview}")

    return {"messages": [response]}


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: DEFINE THE ROUTING FUNCTION (CONDITIONAL EDGE)
# After every agent call, check: did the LLM request a tool call?
#   - YES → route to "tools" node
#   - NO  → route to END (final answer ready)
# ═══════════════════════════════════════════════════════════════════════════

def should_continue(state: AgentState) -> str:
    """
    Conditional edge function — determines the next node to visit.

    Returns:
        "tools"  if the last message contains tool_calls
        "end"    if the LLM produced a final text answer
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"[Router] → Routing to tools ({len(last_message.tool_calls)} call(s))")
        return "tools"

    print("[Router] → No more tool calls. Routing to END.")
    return "end"


# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: BUILD THE GRAPH
# ═══════════════════════════════════════════════════════════════════════════

def build_graph() -> StateGraph:
    """
    Assemble and compile the LangGraph StateGraph.

    Graph topology:
      START → agent_node ─── should_continue ──► tools → agent_node
                                               └──► END

    Returns:
        Compiled LangGraph application ready to invoke.
    """
    # ── 6a. Initialise graph with our state schema ─────────────────────
    graph = StateGraph(AgentState)

    # ── 6b. Add nodes ──────────────────────────────────────────────────
    graph.add_node("agent", agent_node)

    # ToolNode is a prebuilt LangGraph node that:
    #   - reads tool_calls from the last message
    #   - executes each tool function
    #   - appends ToolMessage results back to state
    graph.add_node("tools", ToolNode(TOOLS))

    # ── 6c. Set entry point ────────────────────────────────────────────
    graph.set_entry_point("agent")

    # ── 6d. Add conditional edge from agent ───────────────────────────
    # After agent runs, call should_continue to decide next step
    graph.add_conditional_edges(
        source="agent",
        path=should_continue,
        path_map={
            "tools": "tools",   # tool calls → execute tools
            "end":   END,       # no tool calls → done
        }
    )

    # ── 6e. Add fixed edge: after tools → always back to agent ────────
    graph.add_edge("tools", "agent")

    # ── 6f. Compile ────────────────────────────────────────────────────
    app = graph.compile()
    print("[Graph] ✓ LangGraph agent compiled successfully.")
    return app
