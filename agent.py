"""The deep agent that `langgraph dev` serves for Module 2.

This is the research agent from Module 1, packaged as a file so the LangGraph
server can load it (see `langgraph.json`). What differs from the notebook:

- No `checkpointer`: the server persists every thread for you.
- Two graphs: `research_agent` runs freely, and `research_agent_approval`
  pauses before every file write so a person can approve or reject it.
- `TodoListMiddleware` adds the `write_todos` planning tool. Current deepagents
  releases leave planning opt-in, and Module 2 shows the plan in a UI panel.
"""

from datetime import datetime

from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.tools import tool

from utils.models import model
from utils.search import resilient_web_research


@tool(parse_docstring=True)
def web_research(query: str) -> str:
    """Research a question on the web and return a cited answer.

    Args:
        query: The question or topic to research.
    """
    return resilient_web_research(query, max_retries=2)


research_subagent = {
    "name": "research-agent",
    "description": "Delegate research tasks. Give one topic at a time.",
    "system_prompt": f"""You are a research assistant. Today is {datetime.now().strftime('%Y-%m-%d')}.
Use tools to gather information. Keep findings short, with inline citations.
Limit to 1 search call.""",
    "tools": [web_research],
}

SYSTEM_PROMPT = """You are a research coordinator.
For multi-step requests, plan with write_todos first and keep the todos up to date.
Delegate research to the research-agent with the task() tool.
Keep replies short."""

agent = create_deep_agent(
    model=model,
    tools=[web_research],
    subagents=[research_subagent],
    system_prompt=SYSTEM_PROMPT,
    middleware=[TodoListMiddleware()],
)

approval_agent = create_deep_agent(
    model=model,
    tools=[web_research],
    subagents=[research_subagent],
    system_prompt=SYSTEM_PROMPT,
    middleware=[TodoListMiddleware()],
    interrupt_on={"write_file": True, "edit_file": True},
)
