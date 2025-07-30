from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_core.tools import Tool
import json

class ResearchAgent:
    def __init__(self):
        arxiv_api = ArxivAPIWrapper(
            top_k_results=3,
            ARXIV_MAX_QUERY_LENGTH=300,
            load_max_docs=3,
            load_all_available_meta=False,
            doc_content_chars_max=50000
        )
        self.arxiv_tool = Tool(
            name="Arxiv Search",
            func=arxiv_api.run,
            description="Search Arxiv for research papers."
        )

    async def search(self, query: str) -> str:
        try:
            result = self.arxiv_tool.run(query)
            papers = []
            for paper in result.split("\n\n")[:3]:  # 3 papers max for simplicity
                lines = paper.split("\n")
                title = next((line.split(": ", 1)[1] for line in lines if line.startswith("Title: ")), "Untitled")
                summary = next((line.split(": ", 1)[1] for line in lines if line.startswith("Summary: ")), "No summary")
                papers.append({"title": title, "summary": summary})
            return json.dumps(papers)
        except Exception as e:
            return json.dumps({"error": f"Arxiv search failed: {str(e)}"})
