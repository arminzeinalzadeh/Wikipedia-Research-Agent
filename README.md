# Wikipedia Research Agent

An intelligent agent that answers questions by searching, navigating, and extracting content from Wikipedia. Built with **LangGraph**, **LangChain**, and **Streamlit**, it combines a multi‑tool reasoning engine with an interactive chat interface.



## Features

- **Smart Search** – finds the best Wikipedia page for your query.
- **Section Discovery** – retrieves the complete section tree of any page (including subsections).
- **Deep Content Extraction** – fetches the full text of any section (top‑level or nested).
- **Interactive Chat** – easy‑to‑use Streamlit interface with conversation history.


## How It Works

The agent uses **three specialised tools** to answer factual questions:

| Tool | Purpose |
|------|---------|
| **`wikipedia_search(query)`** | Returns the introductory summary of a page. If the exact title is not found, it searches and returns the top result’s summary. |
| **`wikipedia_page_sections(title)`** | Returns a **complete tree** of all sections and subsections of a page, with indentation showing the hierarchy. |
| **`wikipedia_section_content(title, section_title)`** | Fetches the full text of a specific section (searches at all levels). If the section is not found, it lists all available sections. |

### Agent Workflow

1. **Understand the question** – the agent extracts the main subject from the user’s query.
2. **Get the page summary** – calls `wikipedia_search` with the subject.
3. **Check if the summary answers the question** – if yes, it returns the answer.
4. **Explore the page structure** – if more detail is needed, it calls `wikipedia_page_sections` to see what sections exist.
5. **Retrieve the relevant section** – based on the section list, it calls `wikipedia_section_content` to get the full text.
6. **Answer the question** – the agent extracts the required information (e.g., counting albums, finding dates) and returns a clear final answer.


## Architecture

```
┌─────────────────┐
│   Streamlit UI  │  (User interface)
└────────┬────────┘
         │
┌─────────────────┐
│   LangGraph     │  (State machine with tools)
│   ┌───────────┐ │
│   │   Agent   │ │  (LLM + system prompt)
│   └─────┬─────┘ │
│         │       │
│   ┌───────────┐ │
│   │ ToolNode │ │  (Executes tool calls)
│   └───────────┘ │
└─────────────────┘
         │
┌─────────────────┐
│  Wikipedia API  │  (via wikipediaapi library)
└─────────────────┘
```

- **State Graph** – manages the conversation flow, alternating between the agent and tools.
- **LLM** – a language model that decides which tool to call and interprets the results.
- **ToolNode** – executes the three Wikipedia tools and returns the results to the agent.



## Project Structure

```
.
├── app.py                
├── tools.py              
├── llm.py                
├── streamlit_app.py      
├── requirements.txt      
└── README.md             
```