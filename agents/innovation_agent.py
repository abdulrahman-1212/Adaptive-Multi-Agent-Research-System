import re
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import streamlit as st

# load_dotenv()

class InnovationAgent:
    def __init__(self, model_name: str = "llama3-70b-8192", temperature: float = 0.7):
        """Initialize with Groq LLM for topic generation"""
        try:
            groq_api_key = st.secrets["groq"]["api_key"]
            self.llm = ChatGroq(
                model=model_name,
                api_key=groq_api_key,
                temperature=temperature
            )
            self.output_parser = StrOutputParser()
        except Exception as e:
            print(f"Error initializing LLM: {e}. Falling back to rule-based generation.")
            self.llm = None

    def parse_report(self, report: str) -> Dict:
        """Parse the AnalysisAgent report to extract topic, cluster terms, and gaps"""
        parsed_data = {
            'topic': 'research',
            'cluster_terms': {},
            'gaps': []
        }
        topic_match = re.search(r'\*\*Inferred Topic\*\*: (.*?)\n', report)
        if topic_match:
            parsed_data['topic'] = topic_match.group(1).strip()
        cluster_sections = re.finditer(r'### Cluster (\d+)\n([\s\S]*?)\*\*Common terms\*\*: (.*?)\n', report)
        for cluster in cluster_sections:
            cluster_id = int(cluster.group(1)) - 1
            terms = [t.strip() for t in cluster.group(3).split(',')]
            parsed_data['cluster_terms'][cluster_id] = terms
        gaps_section = re.search(r'## Research Gaps\n([\s\S]*?)(?=\n##|\Z)', report)
        if gaps_section:
            gap_lines = gaps_section.group(1).split('\n')
            for line in gap_lines:
                gap_match = re.match(r'- (.*?)$', line.strip())
                if gap_match:
                    parsed_data['gaps'].append(gap_match.group(1).strip())
        return parsed_data

    def suggest_topics(self, report: str) -> str:
        """Suggest innovative research topics using LLM reasoning"""
        if not report:
            return "# Suggested Research Topics\nNo report provided to suggest topics."

        # Parse the report
        parsed_data = self.parse_report(report)
        topic = parsed_data['topic']
        cluster_terms = parsed_data['cluster_terms']
        gaps = parsed_data['gaps']

        all_terms = [term for terms in cluster_terms.values() for term in terms]
        prompt_template = PromptTemplate(
            input_variables=["topic", "gaps", "cluster_terms"],
            template="""You are an expert researcher tasked with proposing innovative research topics based on an analysis of recent literature. The inferred topic is "{topic}". The analysis identified the following research gaps: {gaps}. Dominant themes include: {cluster_terms}. Propose 3-5 specific, innovative, and actionable research topics that address the gaps and build on the dominant themes. Each topic should be concise, forward-looking, and relevant to the inferred topic. Format as a numbered list."""
        )
        prompt = prompt_template.format(
            topic=topic,
            gaps=", ".join(gaps) if gaps else "none identified",
            cluster_terms=", ".join(all_terms) if all_terms else "none identified"
        )

        suggested_topics = ["# Suggested Research Topics", f"**Based on Topic**: {topic}"]
        if self.llm:
            try:
                response = self.llm.invoke(prompt)
                topics_text = self.output_parser.parse(response.content)
                topics = [t.strip() for t in topics_text.split('\n') if t.strip().startswith(('-', '1.', '2.', '3.', '4.', '5.'))]
                topics = [re.sub(r'^- |\d+\.\s*', '', t) for t in topics]  # Clean numbering/bullets
                topics = [t for t in topics if t]  # Remove empty
            except Exception as e:
                print(f"LLM generation failed: {e}. Using fallback.")
                topics = []
        else:
            topics = []

        suggested_topics.append("\n## Proposed Topics")
        for i, topic in enumerate(topics[:5], 1):
            suggested_topics.append(f"{i}. {topic}")

        return '\n'.join(suggested_topics)
