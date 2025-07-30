import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

# load_dotenv()

class AnalysisAgent:
    def __init__(self, model_name: str = "llama3-70b-8192"):
        groq_api_key = st.secrets["groq"]["api_key"]
        self.llm = ChatGroq(
            model=model_name,
            api_key=groq_api_key,
            temperature=0.7
        )

    async def analyze(self, research_data: str) -> str:
        prompt_template = PromptTemplate(
            input_variables=["research_data"],
            template="""Analyze the following research data: {research_data}
            Identify key themes, clusters, and gaps. Format as markdown:
            **Inferred Topic**: [Topic]
            ### Cluster 1
            **Common terms**: [Terms]
            ## Research Gaps
            - [Gap 1]
            - [Gap 2]"""
        )
        prompt = prompt_template.format(research_data=research_data)
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            return f"Error in analysis: {str(e)}"
