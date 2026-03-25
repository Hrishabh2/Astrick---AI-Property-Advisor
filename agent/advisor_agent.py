"""
agent/advisor_agent.py
----------------------
AutoGen 0.7.5 agent wiring for the AI Property Advisor.

Uses:
  - autogen_agentchat  (0.7.5 package name: pyautogen >= 0.7.5 or autogen-agentchat)
  - AssistantAgent with tool registration
  - OpenAI-compatible client pointing to Groq
"""

from __future__ import annotations
import json
import asyncio
from typing import Any

# AutoGen 0.4+ (autogen-agentchat 0.4.x maps to the 0.7.5 release series)
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient


from config.settings import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, TEMPERATURE
from agent.system_prompt import SYSTEM_PROMPT

from tools.property_tools import (
    recommend_property,
    compare_locations,
    investment_advice,
    update_user_profile,
    get_user_profile,
    web_search,
)


def _build_llm_client() -> OpenAIChatCompletionClient:
    """Create an OpenAI-compatible client pointed at Groq's API."""
    return OpenAIChatCompletionClient(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        model_capabilities={
            "vision": False,
            "function_calling": True,
            "json_output": True,
        },
        temperature=TEMPERATURE,
    )


def build_agent() -> AssistantAgent:
    """
    Instantiate the PropertyAdvisor AssistantAgent with all tools registered.
    Returns a fresh agent (stateless per call; memory handled by tools).
    """
    client = _build_llm_client()

    agent = AssistantAgent(
        name="PropertyAdvisor",
        model_client=client,
        tools=[
            recommend_property,
            compare_locations,
            investment_advice,
            update_user_profile,
            get_user_profile,
            web_search,
        ],
        system_message=SYSTEM_PROMPT,
        reflect_on_tool_use=True,  
        model_client_stream=False,
    )
    return agent


async def get_agent_response(
    agent: AssistantAgent,
    user_message: str,
    session_id: str,
    history: list[dict],
) -> str:
    """
    Send a user message to the agent and return its textual reply.

    Args:
        agent        : The AssistantAgent instance (re-used across turns)
        user_message : Latest user input string
        session_id   : Unique session id (injected into messages for tool use)
        history      : Previous conversation turns for context

    Returns:
        Agent's response as a plain string.
    """
    # Inject session_id so tools can access the right profile
    enriched_msg = f"[session_id={session_id}]\n\n{user_message}"

    cancellation_token = CancellationToken()

    response = await agent.on_messages(
        [TextMessage(content=enriched_msg, source="user")],
        cancellation_token=cancellation_token,
    )

    # Extract text from the last inner message
    reply = response.chat_message.content
    if isinstance(reply, list):
        # Handle structured content blocks
        texts = [
            block.text if hasattr(block, "text") else str(block)
            for block in reply
            if hasattr(block, "text") or isinstance(block, str)
        ]
        reply = " ".join(texts)

    return str(reply).strip()


def run_agent_sync(
    agent: AssistantAgent,
    user_message: str,
    session_id: str,
    history: list[dict],
) -> str:
    """
    Synchronous wrapper around get_agent_response for use in Streamlit.

    WHY THIS APPROACH:
    Streamlit executes each script run in a plain worker thread (ScriptRunner)
    that has NO asyncio event loop attached.  Calling asyncio.get_event_loop()
    inside such a thread raises "There is no current event loop in thread …".
    asyncio.run() creates a fresh loop but is blocked when an outer loop already
    exists (e.g. in Jupyter).

    SOLUTION — run the coroutine on a brand-new event loop in a dedicated
    background thread.  This works in every host environment:
      • Streamlit (no loop in thread)   
      • Jupyter / IPython (loop running) 
      • Plain Python scripts             
    """
    import concurrent.futures

    result_holder: list[str] = []
    error_holder:  list[Exception] = []

    def _run_in_thread():
        # Each background thread gets its own brand-new event loop.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                get_agent_response(agent, user_message, session_id, history)
            )
            result_holder.append(result)
        except Exception as exc:
            error_holder.append(exc)
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        future.result()   # blocks until the thread finishes (re-raises exceptions)

    if error_holder:
        return f" Agent encountered an error: {error_holder[0]}"

    return result_holder[0] if result_holder else " No response received from agent."