import streamlit as st
import asyncio
import pandas as pd
from agents.research_mas import ResearchMAS

# Set page configuration with dark theme
st.set_page_config(page_title="Multi-Agent Research System", layout="wide", initial_sidebar_state="collapsed")

# Manually set dark theme
st.markdown(
    """
    <style>
    /* Set the background color */
    .css-18e3th9 {
        background-color: #1a1a1a;
        color: white;
    }
    
    /* Set the color of titles and headers */
    .css-1v0mbdj, .css-1ka6r26 {
        color: white !important;
    }
    
    /* Set the color of text and input fields */
    .stTextInput input {
        background-color: #333333;
        color: white;
    }
    
    /* Set button color */
    .stButton>button {
        background-color: #444444;
        color: white;
    }
    
    /* Set the sidebar background color */
    .css-1d391kg {
        background-color: #333333;
        color: white;
    }

    /* Set expander background */
    .stExpanderHeader {
        background-color: #444444;
        color: white;
    }

    /* Set expander content text */
    .stExpanderContent {
        color: white;
    }

    /* Set success and info text color */
    .stSuccess, .stInfo {
        color: white;
    }

    /* Set markdown color */
    .markdown {
        color: white;
    }

    </style>
    """, unsafe_allow_html=True
)

# Initialize Multi-Agent System
mas = ResearchMAS()

if "results" not in st.session_state:
    st.session_state.results = []

async def run_mas(query: str):
    try:
        with st.spinner("Fetching papers from Arxiv and processing..."):
            result = await mas.run(query)
        return result
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

# Streamlit UI
st.title("Multi-Agent Research System")
st.markdown("Search Arxiv for research papers and generate insights using a multi-agent system powered by Llama3.")

query = st.text_input("Enter your research query:", placeholder="e.g., AI in healthcare")
col1, col2 = st.columns([1, 1])
with col1:
    submit_button = st.button("Submit Query")
with col2:
    clear_button = st.button("Clear Results")

if clear_button:
    st.session_state.results = []
    st.success("Results cleared.")

if submit_button and query:
    result = asyncio.run(run_mas(query))
    if result:
        if "Error in analysis" in result["analysis_report"] or "LLM generation failed" in result["suggested_topics"]:
            st.warning("Some results used fallback mechanisms due to issues with the Groq API.")
        st.session_state.results.append({
            "query": query,
            "search_results": result["search_results"],
            "analysis_report": result["analysis_report"],
            "suggested_topics": result["suggested_topics"]
        })

st.header("Research Results")
if not st.session_state.results:
    st.info("No results yet. Submit a query to see results.")
else:
    for idx, result in enumerate(st.session_state.results):
        with st.expander(f"Query {idx + 1}: {result['query']}", expanded=True):
            st.subheader("Research Papers (Arxiv)")
            if isinstance(result["search_results"], list) and result["search_results"]:
                df = pd.DataFrame(result["search_results"])
                st.dataframe(df[["title", "summary"]], use_container_width=True)
            else:
                st.write("No papers found or error in search.")
            
            st.subheader("Analysis Report")
            st.markdown(result["analysis_report"])
            
            st.subheader("Suggested Topics")
            st.markdown(result["suggested_topics"])

st.markdown("---")
st.markdown("Powered by LangGraph, Arxiv, and Groq (Llama3-70b-8192)")
