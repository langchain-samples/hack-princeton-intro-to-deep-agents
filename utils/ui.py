"""Print helpers that stand in for UI panels in Module 2.

Module 2 plays the part of a chat UI. The notebook makes the SDK calls; these
helpers only turn what comes back into something that looks like the panel a
real frontend would draw (sidebar, chat bubble, plan, file browser, approval
card). Nothing here talks to the server.
"""

from __future__ import annotations

from typing import Any

TODO_ICONS = {"completed": "[x]", "in_progress": "[~]", "pending": "[ ]"}

# tool_call_id -> tool name, so a result can be labeled even when it arrives without a name.
_tool_names: dict[str, str] = {}


def text_of(message: dict) -> str:
    """Return the text of a message dict, whether content is a string or blocks."""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def file_text(file_data: Any) -> str:
    """Return a virtual file's text. Deep agents store files as dicts with `content`."""
    content = file_data.get("content") if isinstance(file_data, dict) else file_data
    if isinstance(content, list):
        return "\n".join(content)
    return str(content or "")


def short(text: str, limit: int = 80) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render_sidebar(user: str, threads: list[dict]) -> None:
    print(f"┌─ {user.title()}'s conversations " + "─" * 30)
    for t in threads:
        title = (t.get("metadata") or {}).get("title", "(untitled)")
        print(f"│  • {title:<34} {t['status']}")
    print("└" + "─" * 55)


def render_plan(todos: list[dict]) -> None:
    print("  ┌─ PLAN " + "─" * 40)
    for todo in todos:
        print(f"  │ {TODO_ICONS.get(todo.get('status'), '[?]')} {todo.get('content')}")
    print("  └" + "─" * 47)


def render_files(files: dict) -> None:
    print("  ┌─ FILES " + "─" * 39)
    for path, data in files.items():
        lines = file_text(data).count("\n") + 1
        print(f"  │ {path}  ({lines} lines)")
    print("  └" + "─" * 47)


def describe_messages(messages: list[dict], prefix: str = "") -> None:
    """Print one line per tool call or tool result, the activity feed of a chat UI."""
    for m in messages or []:
        if m.get("type") == "ai":
            for call in m.get("tool_calls") or []:
                _tool_names[call.get("id")] = call["name"]
                args = call.get("args") or {}
                hint = args.get("subagent_type") or args.get("query") or args.get("file_path") or ""
                print(f"{prefix}→ calls {call['name']}({short(hint, 50)})")
            if text_of(m) and not m.get("tool_calls"):
                print(f"{prefix}💬 {short(text_of(m), 100)}")
        elif m.get("type") == "tool":
            name = m.get("name") or _tool_names.get(m.get("tool_call_id"), "tool")
            print(f"{prefix}← {name} returned {len(text_of(m))} chars")


def render_update(update: dict | None, prefix: str = "") -> None:
    """Render one `updates` stream event: activity, then plan and files if they changed."""
    if not isinstance(update, dict):
        return
    describe_messages(update.get("messages"), prefix)
    if update.get("todos"):
        render_plan(update["todos"])
    if update.get("files"):
        render_files(update["files"])


def render_approval_card(interrupt: dict) -> None:
    """Draw the approve / edit / reject card for a deep agent `interrupt_on` pause."""
    value = interrupt.get("value", {})
    configs = {c.get("action_name"): c for c in value.get("review_configs", [])}
    for action in value.get("action_requests", []):
        allowed = configs.get(action["name"], {}).get("allowed_decisions", ["approve", "edit", "reject"])
        print("┌─ ⚠ The agent wants to run a tool " + "─" * 20)
        print(f"│  tool: {action['name']}")
        for key, val in (action.get("args") or {}).items():
            print(f"│  {key}: {short(val, 60)}")
        print("│")
        print("│  " + "   ".join(f"[ {d.title()} ]" for d in allowed))
        print("└" + "─" * 55)


def render_transcript(messages: list[dict]) -> None:
    """Rebuild the chat view from saved thread state: user and assistant turns only."""
    for m in messages:
        text = text_of(m)
        if m.get("type") == "human":
            print(f"🧑 {short(text, 100)}")
        elif m.get("type") == "ai" and text:
            print(f"🤖 {short(text, 100)}")
