"""
Real MCP client: launches mcp_server/stock_tools.py as a subprocess and talks
to it over the actual MCP protocol (stdio transport), rather than importing
the tool functions directly. This is what makes the "MCP" part of the demo
genuine — the harness is a real MCP client, and stock_tools.py could equally
be plugged into Claude Desktop or any other MCP-compatible host unmodified.

Streamlit is synchronous, so each call spins up a short-lived asyncio event
loop. For a demo's tool-call volume this is simple and reliable; a
production app would keep one long-lived session open instead.
"""

import os
import sys
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "stock_tools.py")


def _flatten_exception(exc: BaseException) -> str:
    """Python's asyncio TaskGroup (and anyio) wrap the real failure inside an
    ExceptionGroup, so a bare `str(exc)` just says "unhandled errors in a
    TaskGroup (1 sub-exception)" with no useful detail. Walk into it and
    return the innermost, actually-useful error message(s)."""
    messages = []

    def walk(e: BaseException):
        if hasattr(e, "exceptions"):  # ExceptionGroup / BaseExceptionGroup (Python 3.11+)
            for sub in e.exceptions:
                walk(sub)
        else:
            messages.append(f"{type(e).__name__}: {e}")

    walk(exc)
    return "; ".join(messages) if messages else str(exc)


async def _call_tool_async(tool_name: str, arguments: dict) -> dict:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )
    # Note: not all versions of the `mcp` package's stdio_client() accept an
    # `errlog` kwarg for capturing subprocess stderr, so we don't rely on
    # that — the exception-unwrapping below is what actually surfaces the
    # real error instead of the generic "TaskGroup" message.
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                # MCP tool results come back as a list of content blocks; our
                # tools return a single JSON-serializable dict via structured
                # content, so unpack it accordingly.
                if result.structuredContent is not None:
                    return result.structuredContent
                # Fallback: parse the first text block as JSON.
                for block in result.content:
                    if hasattr(block, "text"):
                        try:
                            return json.loads(block.text)
                        except json.JSONDecodeError:
                            return {"raw": block.text}
                return {}
    except BaseException as e:
        raise RuntimeError(_flatten_exception(e)) from e


async def _list_tools_async() -> list[str]:
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [t.name for t in tools.tools]


def call_tool(tool_name: str, arguments: dict) -> dict:
    """Synchronous wrapper for use inside Streamlit callbacks."""
    return asyncio.run(_call_tool_async(tool_name, arguments))


def list_tools() -> list[str]:
    return asyncio.run(_list_tools_async())
