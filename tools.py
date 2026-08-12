import re

from langchain_core.tools import tool
import wikipediaapi
from wikipediaapi import WikipediaException

# Handle specific error types
# from wikipediaapi import , WikiConnectionError, WikiHttpTimeoutError, WikiHttpError, WikiInvalidJsonError, WikiRateLimitError


# Helper function to recursively collect section titles with indentation
def _collect_sections(section_list, indent=0):
    """
    Recursively traverse a list of Section objects and return a string
    with each section title indented by its depth.
    """
    lines = []
    for section in section_list:
        prefix = "  " * indent
        lines.append(f"{prefix}• {section.title}")
        # Recurse into subsections (section.sections is a list of Section)
        if section.sections:
            lines.extend(_collect_sections(section.sections, indent + 1))
    return lines


@tool
def wikipedia_search(page_title: str) -> str:
    """
    Searches Wikipedia and returns the introductory summary of the page.
    If the exact title does not exist, it falls back to a full_text search
    and returns the top result's summary.

    Args:
        query (str): The Wikipedia page title to look up.

    Returns:
        str: The page summary, disambiguation options, or search results.
    """
    wiki = wikipediaapi.Wikipedia(user_agent='Agentic AI', language='en')
    try:
        page = wiki.page(page_title)
        if page.exists():
            if page.title.endswith("(disambiguation)"):
                links = list(page.links.keys())[:10]
                return f"Disambiguation page. Possible topics: {', '.join(links)}"
            summary = page.summary
            if len(summary) > 1500:
                summary = summary[:1500] + "... (truncated)"
            return summary

        # No exact match – search and fetch top result
        search_results = wiki.search(page_title, limit=1)
        if search_results.totalhits == 0:
            return f"No results found for '{page_title}'."
        top_title = next(iter(search_results.pages.keys()))
        top_page = wiki.page(top_title)
        if top_page.exists():
            if top_page.title.endswith("(disambiguation)"):
                links = list(top_page.links.keys())[:10]
                return f"Disambiguation page. Possible topics: {', '.join(links)}"
            summary = top_page.summary
            if len(summary) > 1500:
                summary = summary[:1500] + "... (truncated)"
            return f"Showing page for '{top_title}':\n{summary}"
        else:
            snippet = search_results.pages[top_title].search_meta.snippet or ""
            snippet = re.sub(r'<[^>]+>', '', snippet)
            return f"Top result: {top_title} – {snippet[:500]}..."
    except WikipediaException as e:
        return f"Wikipedia API error: {e}"

@tool
def wikipedia_page_sections(page_title: str) -> str:
    """
    Returns a complete list of all sections and subsections on a Wikipedia page,
    with indentation showing the hierarchy.

    Use this to discover which sections exist on a page before fetching their content.

    Args:
        page_title (str): The exact title of the Wikipedia page.

    Returns:
        str: A tree of section titles (one per line, indented), or an error message.
    """
    wiki = wikipediaapi.Wikipedia(user_agent='Agentic AI', language='en')
    try:
        page = wiki.page(page_title)
        if not page.exists():
            return f"Page '{page_title}' does not exist."
        if page.title.endswith("(disambiguation)"):
            return f"'{page_title}' is a disambiguation page. Use wikipedia_search to get options."

        if not page.sections:
            return f"Page '{page_title}' has no sections."

        # Build the section tree
        lines = _collect_sections(page.sections)
        return f"Sections on '{page_title}':\n" + "\n".join(lines)

    except WikipediaException as e:
        return f"Wikipedia API error: {e}"
    
    # except WikiRateLimitError as e:
    #     print(f"Rate limited in wikipedia_page_sections function! Retry after: {e.retry_after} seconds")
    # except WikiHttpError as e:
    #     print(f"HTTP error in wikipedia_page_sections function {e.status_code}: {e}")
    # except WikiHttpTimeoutError:
    #     print("Request timed out in wikipedia_page_sections function")
    # except WikiConnectionError:
    #     print("Could not connect to Wikipedia in wikipedia_page_sections function")
    # except WikiInvalidJsonError:
    #     print("Received invalid response from Wikipedia in wikipedia_page_sections function")


@tool
def wikipedia_section_content(page_title: str, section_title: str) -> str:
    """
    Returns the full text of a specific section from a Wikipedia page.
    The search is performed at all levels (top_level and nested).
    If the exact section title is found, its text is returned.

    Args:
        page_title (str): The exact title of the Wikipedia page.
        section_title (str): The title of the section (case_sensitive).

    Returns:
        str: The full text of that section, or an error message.
    """
    wiki = wikipediaapi.Wikipedia(user_agent='Agentic AI (your@email.com)', language='en')
    try:
        page = wiki.page(page_title)
        if not page.exists():
            return f"Page '{page_title}' does not exist."

        # Recursively search for the section
        def find_section(sections):
            for sec in sections:
                if sec.title == section_title:
                    return sec
                if sec.sections:
                    found = find_section(sec.sections)
                    if found:
                        return found
            return None

        target = find_section(page.sections)
        if target is None:
            # Optionally list all section titles to help the agent correct its query
            all_titles = []
            def collect_all(sections):
                for sec in sections:
                    all_titles.append(sec.title)
                    if sec.sections:
                        collect_all(sec.sections)
            collect_all(page.sections)
            return f"Section '{section_title}' not found. Available sections: {', '.join(all_titles)}"

        text = target.text
        if len(text) > 5000:
            text = text[:5000] + "... (truncated)"
        return text

    except WikipediaException as e:
        return f"Wikipedia API error: {e}"



# testing
if __name__ == "__main__":
    # Test scenarios covering all edge cases
    test_queries = [
        ("Exact match", "Python_(programming_language)"),
        ("Ambiguous (disambiguation)", "Python"),
        ("Non_existent", "Fjsdklfjsl"),
        ("Famous person", "Albert Einstein"),
        ("Common misspelling", "Alber Einstein"),   # Wikipedia will suggest correct title
    ]

    for description, query in test_queries:
        print(f"\nTesting {description}:")
        print(f"=== (query: '{query}') ===")
        response = wikipedia_search.invoke(query)

        print(response[:100] + ("..." if len(response) > 100 else ""))
        

        