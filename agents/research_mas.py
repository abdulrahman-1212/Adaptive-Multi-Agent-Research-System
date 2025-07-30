import json
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.innovation_agent import InnovationAgent

class ResearchState(TypedDict):
    query: str
    search_results: List[Dict]
    analysis_report: str
    suggested_topics: str

async def research_node(state: ResearchState) -> ResearchState:
    research_agent = ResearchAgent()
    search_results = await research_agent.search(state["query"])
    return {"search_results": json.loads(search_results) if isinstance(search_results, str) else search_results}

async def analysis_node(state: ResearchState) -> ResearchState:
    analysis_agent = AnalysisAgent()
    analysis_report = await analysis_agent.analyze(json.dumps(state["search_results"]))
    return {"analysis_report": analysis_report}

async def innovation_node(state: ResearchState) -> ResearchState:
    innovation_agent = InnovationAgent()
    suggested_topics = innovation_agent.suggest_topics(state["analysis_report"])
    return {"suggested_topics": suggested_topics}

class ResearchMAS:
    def __init__(self, model_name: str = "llama3-70b-8192"):
        """Initialize the MAS workflow with LangGraph"""
        self.model_name = model_name
        workflow = StateGraph(ResearchState)
        workflow.add_node("research", research_node)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("innovation", innovation_node)
        workflow.set_entry_point("research")
        workflow.add_edge("research", "analysis")
        workflow.add_edge("analysis", "innovation")
        workflow.add_edge("innovation", END)
        self.workflow = workflow.compile()

    async def run(self, query: str) -> dict:
        state = {
            "query": query,
            "search_results": [],
            "analysis_report": "",
            "suggested_topics": ""
        }
        result = await self.workflow.ainvoke(state)
        return result