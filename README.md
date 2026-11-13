# Deep Agents Workshop

This repository contains hands-on tutorials for learning Deep Agents.

This is a condensed version of LangChain Academy, intended to be run in a session with a LangChain engineer. If you're interested in going into more depth, or working through tutorials on your own, check out [LangChain Academy](https://academy.langchain.com/)! LangChain Academy has helpful pre-recorded videos from our LangChain engineers.

| Module | Notebook | What you build |
|--------|----------|----------------|
| 1 | `modules/01_deep_agents.ipynb` | A research agent with `create_deep_agent()`: filesystem, planning, subagents, backends, middleware, HITL, AGENTS.md, and skills |
| 2 | `modules/02_deep_agents_sdk.ipynb` | That agent served by a local LangGraph server, driven the way a chat UI would through the LangGraph SDK: threads, streaming tokens, live plan and files, subagent activity, approvals, stop and reconnect |

Module 2 starts a local agent server (`langgraph dev`) from inside the notebook. It serves the graphs listed in `langgraph.json`, which are defined in `agent.py`, and reads your keys from `.env`.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment variables
cp .env.example .env
# Edit .env and fill in your keys
```

| Key | Required for | Get one |
|-----|--------------|---------|
| `ANTHROPIC_API_KEY` | Both modules (default model and the web research tool) | <https://platform.claude.com> |

```bash
# 3. Start Jupyter
uv run jupyter notebook
```

## Web Research Tool

Both modules give the agent a `web_research` tool. It asks Claude to answer the question with **Anthropic's server-side web search tool** (`web_search_20250305`) and returns a short answer followed by the sources it cited. Anthropic runs the searches, so there's no separate search provider or key.

The plumbing lives in `utils/search.py` (`resilient_web_research`). It retries on failure, and if every attempt fails it returns a canned, topic-matched response so a flaky network doesn't stall the workshop. The model that runs the search is `RESEARCH_MODEL` in that file. It's independent of the agent's model, so the tool still needs `ANTHROPIC_API_KEY` if you switch the agent to another provider. Web search isn't available on Amazon Bedrock, so even a Bedrock-backed agent calls the Anthropic API for research.

## Switching Models

Both modules import `model` from `utils/models.py`. Change one block there to swap providers — no notebook edits required.

```python
# utils/models.py

# Anthropic (default)
MODEL_SPEC = {"model": "anthropic:claude-haiku-5-5"}
API_KEY_ENV = "ANTHROPIC_API_KEY"

# OpenAI
# MODEL_SPEC = {"model": "openai:gpt-5.6-luna", "use_responses_api": True}
# API_KEY_ENV = "OPENAI_API_KEY"
```

The default is Claude Haiku 5.5 because it's fast and inexpensive; swap in `claude-sonnet-5-5` or `claude-opus-5-5` for harder tasks. `utils/models.py` also ships commented-out blocks for Azure OpenAI and AWS Bedrock.

## Project Structure

```
hack-princeton-intro-to-deep-agents/
├── README.md
├── pyproject.toml
├── .env.example
├── agent.py                        (the deep agent the Module 2 server runs)
├── langgraph.json                  (tells `langgraph dev` which graphs to serve)
├── utils/
│   ├── models.py                   (the chat model every notebook uses)
│   ├── search.py                   (web research via Anthropic's web search tool)
│   └── ui.py                       (Module 2 printouts that stand in for UI panels)
├── images/                         (diagrams used by the notebooks)
└── modules/
    ├── 01_deep_agents.ipynb        (Module 1)
    └── 02_deep_agents_sdk.ipynb    (Module 2)
```

## Common Issues

**Notebook can't find `utils`**
Each module's setup cell prepends `project_root` (the workshop root) to `sys.path`. If you moved a notebook, update the `Path().resolve().parent` line to point at the workshop root.

**Module 2: the server doesn't start**
The setup cell writes the server's output to `langgraph_dev.log` at the workshop root; the error is usually there. If port 2024 is taken by a server from an earlier session, the cell reuses it. Restart that server (or stop it) after changing `.env` or `agent.py`, since it reads them only at startup.

**Tool output starts with `[fallback content; live search unavailable ...]`**
Every call to the Anthropic API failed. Check that `ANTHROPIC_API_KEY` is set, that your account can use the model named in `RESEARCH_MODEL`, and that web search is enabled for your organization in the Claude Console.
