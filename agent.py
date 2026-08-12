from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

import tools
import llm
from system_prompt import prompt_for_system

class State(TypedDict):
    """State Class"""
    messages: Annotated[Sequence[BaseMessage], add_messages]    

tools = [tools.wikipedia_search, tools.wikipedia_page_sections, tools.wikipedia_section_content]
model = llm.model.bind_tools(tools)

def call_model(state: State) -> State:
    """Send messages to LLM, which may decide to call tools."""
    system_prompt = SystemMessage(content=prompt_for_system)
    # Invoke model with system prompt + conversation history
    response = model.invoke([system_prompt] + list(state["messages"]))
    return {"messages": [response]}

def decide_route(state: State):
    """If last message contains tool_calls, go to tools node; otherwise end."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "continue"
    return "end"


graph = StateGraph(State)
graph.add_node("the_agent", call_model)
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("the_agent")
graph.add_conditional_edges(
    "the_agent",
    decide_route,
    {
        "continue": "tools",
        "end": END,
    },
)
graph.add_edge("tools", "the_agent")

agent = graph.compile()


