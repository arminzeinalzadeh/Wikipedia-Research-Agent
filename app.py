"""Wikipedia Research Agent Streamlit frontend.
This module provides a chat interface for a agent
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent import agent

# Page configuration
st.set_page_config(
    page_title="Wikipedia Research Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS (optional – left‑to‑right, clean styling)
st.markdown(
    """
    <style>
    .main {
        max-width: 800px;
        margin: 0 auto;
    }
    .stChatMessage {
        text-align: left;
    }
    h1, h2, h3 {
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.title("📚 Wikipedia Research Agent")
st.markdown("Ask me anything – I can search Wikipedia, list sections, and retrieve detailed content from any article.")
st.divider()

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Append user message to session
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare the conversation history (as before)
    graph_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            graph_messages.append(HumanMessage(content=msg["content"]))
        else:
            graph_messages.append(AIMessage(content=msg["content"]))

    # Create a placeholder for the trace output
    trace_container = st.expander(" Agent Trace (stream)", expanded=False)
    trace_area = trace_container.empty()   # we'll update this with each step

    # We'll also keep the final assistant response
    assistant_response = ""

    with st.spinner("Thinking and searching Wikipedia..."):
        try:
            # Stream the agent with the same input format as before
            stream = agent.stream({"messages": graph_messages}, stream_mode="values")

            step = 0
            for chunk in stream:
                step += 1
                # Build a string representation of this stream update
                trace_lines = []
                trace_lines.append(f"--- Stream updated {step} Times ---")
                messages = chunk.get("messages", [])
                # Show the last few messages (or all, depending on your needs)
                for msg in messages:   # can modify to see last messages
                    if isinstance(msg, tuple):
                        role, content = msg
                        trace_lines.append(f"{role.upper()}: {content}")
                    else:
                        # Try to get a pretty representation
                        if hasattr(msg, "pretty_repr"):
                            pretty = msg.pretty_repr(html=False)
                            trace_lines.append(pretty)
                        else:
                            role = getattr(msg, "role", getattr(msg, "type", "assistant"))
                            content = getattr(msg, "content", str(msg))
                            trace_lines.append(f"{role}: {content}")
                        # Show tool calls if any
                        tool_calls = getattr(msg, "tool_calls", None)
                        if tool_calls:
                            trace_lines.append("Tool calls:")
                            for tc in tool_calls:
                                trace_lines.append(f"  - {tc}")

                # Update the trace area with all steps so far
                trace_area.text("\n".join(trace_lines))

                # The final message in the last chunk should be the assistant's answer
                # but we can also capture it at the end
                # We'll store the last non‑tool message content as the final answer
                last_msg = messages[-1] if messages else None
                if last_msg and hasattr(last_msg, "content") and not getattr(last_msg, "tool_calls", None):
                    assistant_response = last_msg.content

            # If for some reason we didn't capture a response, fallback to the last content
            if not assistant_response and chunk and chunk.get("messages"):
                assistant_response = chunk["messages"][-1].content

            # Append assistant response to session
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

        except Exception as e:
            error_msg = f"❌ An error occurred: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)