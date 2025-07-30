# Design Documentation: Multi-Agent Research System

## Overview
The Multi-Agent Research System is a Streamlit-based web application designed to facilitate academic research by leveraging a multi-agent system (MAS) orchestrated via LangGraph. It integrates three specialized agents: `ResearchAgent` for fetching research papers from Arxiv, `AnalysisAgent` for analyzing retrieved data, and `InnovationAgent` for proposing novel research topics. The system uses the Groq API with the Llama3 model (`llama3-70b-8192`) for inference and stores results in Streamlit's session state, avoiding the need for a persistent database.

This document outlines the system architecture, agent communication protocol, custom algorithms, innovations, limitations, and future work.

## System Architecture

### Components
1. **Streamlit Frontend (`app.py`)**:
   - A web-based user interface built with Streamlit, providing input fields for research queries, buttons for submitting queries and clearing results, and a display for results in tabular and markdown formats.
   - Uses `st.session_state` to store query results temporarily, ensuring no database dependency.
   - Handles asynchronous MAS execution via `asyncio.run`.

2. **Multi-Agent System (MAS, `research_mas.py`)**:
   - Orchestrated using LangGraph, a library for building stateful, graph-based workflows.
   - Defines a `ResearchState` (TypedDict) to manage the state across agents: `query`, `search_results`, `analysis_report`, and `suggested_topics`.
   - Implements a sequential workflow: `ResearchAgent` → `AnalysisAgent` → `InnovationAgent`.

3. **Agents**:
   - **ResearchAgent (`research_agent.py`)**:
     - Uses `langchain_community.utilities.arxiv.ArxivAPIWrapper` to fetch up to three research papers from Arxiv based on the user’s query.
     - Outputs JSON-formatted results with `title` and `summary` fields.
   - **AnalysisAgent (`analysis_agent.py`,)**:
     - Uses `langchain_groq.ChatGroq` with `llama3-70b-8192` to analyze Arxiv results, producing a markdown report with inferred topics, clusters, and research gaps.
   - **InnovationAgent (`innovation_agent.py`)**:
     - Uses `langchain_groq.ChatGroq` with `llama3-70b-8192` to generate 3-5 innovative research topics based on the analysis report.
     - Includes a rule-based fallback mechanism for robustness if the Groq API fails.

4. **Environment Configuration**:
   - `.env`: Stores the Groq API key securely.
   - `requirements.txt`: Lists dependencies (`streamlit`, `langchain-groq`, `langgraph`, `python-dotenv`, `langchain-community`).

### Architecture Diagram
```
[User]
   |
   v
[Streamlit Frontend (app.py)]
   | - Query Input
   | - Session State Storage
   | - Result Display (Table, Markdown)
   |
   v
[LangGraph Workflow (research_mas.py)]
   | - ResearchState: {query, search_results, analysis_report, suggested_topics}
   |
   v
[ResearchAgent] ----> [AnalysisAgent] ----> [InnovationAgent]
   | - Arxiv API       | - Groq API         | - Groq API
   |                   | - Llama3           | - Llama3
   |                   |                    | - Fallback
   v                   v                    v
[JSON Output] ----> [Markdown Report] ----> [Markdown Topics]
```

### Data Flow
1. User submits a query via the Streamlit frontend.
2. The query is passed to `ResearchMAS`, initializing a `ResearchState`.
3. `ResearchAgent` fetches Arxiv papers, storing results as JSON in `search_results`.
4. `AnalysisAgent` processes `search_results`, generating a markdown `analysis_report`.
5. `InnovationAgent` processes `analysis_report`, producing `suggested_topics` in markdown.
6. Results are stored in `st.session_state.results` and displayed in the Streamlit UI.

## Agent Communication Protocol

### Overview
The agents communicate through a state-based protocol managed by LangGraph, using the `ResearchState` TypedDict as a shared state object. Each agent operates as a node in a directed acyclic graph (DAG), passing data sequentially without direct inter-agent messaging.

### Protocol Details
- **State Management**:
  - `ResearchState` fields:
    - `query`: String, the user’s input query (e.g., "AI in healthcare").
    - `search_results`: List of dictionaries, JSON-formatted Arxiv results (`title`, `summary`).
    - `analysis_report`: String, markdown-formatted analysis output.
    - `suggested_topics`: String, markdown-formatted list of research topics.
  - LangGraph ensures state immutability between nodes, updating `ResearchState` after each agent’s execution.

- **Communication Flow**:
  1. **ResearchAgent**:
     - Input: `ResearchState.query`.
     - Output: Updates `ResearchState.search_results` with JSON (e.g., `[{"title": "...", "summary": "..."}, ...]`).
     - Method: Async call to `ArxivAPIWrapper.run`, parsed into JSON.
  2. **AnalysisAgent**:
     - Input: `ResearchState.search_results` (JSON string).
     - Output: Updates `ResearchState.analysis_report` with markdown (e.g., `**Inferred Topic**: ...`).
     - Method: Async call to `ChatGroq.ainvoke` with a prompt template.
  3. **InnovationAgent**:
     - Input: `ResearchState.analysis_report` (markdown string).
     - Output: Updates `ResearchState.suggested_topics` with markdown (e.g., `# Suggested Research Topics\n1. ...`).
     - Method: Synchronous call to `ChatGroq.invoke` (or fallback rules), parsing markdown.

- **Error Handling**:
  - `ResearchAgent`: Returns JSON with an `error` field if the Arxiv API fails.
  - `AnalysisAgent`: Returns an error string if the Groq API fails.
  - `InnovationAgent`: Uses a rule-based fallback if the Groq API fails, ensuring 3-5 topics are always generated.
  - Streamlit displays errors via `st.error` and warns if fallbacks are used.

- **Asynchronous Operations**:
  - `ResearchAgent` and `AnalysisAgent` use async methods (`ainvoke`) for non-blocking API calls.
  - `InnovationAgent` uses synchronous `invoke` due to its fallback mechanism, but this is compatible with LangGraph’s async workflow.
  - Streamlit uses `asyncio.run` to handle async calls, with potential for threading in production.

## Custom Algorithms

### 1. Arxiv Result Parsing (`ResearchAgent`)
- **Description**: Parses raw Arxiv API output into a structured JSON format.
- **Implementation**:
  - Splits the Arxiv response (newline-separated paper entries) into individual papers.
  - Extracts `title` and `summary` fields using string splitting and defaults (`"Untitled"`, `"No summary"`) for missing data.
  - Limits output to 3 papers for consistency.
  - Returns JSON string: `[{"title": "...", "summary": "..."}, ...]`.
- **Purpose**: Ensures compatibility with `AnalysisAgent` by standardizing Arxiv output.

### 2. Analysis Report Generation (`AnalysisAgent`)
- **Description**: Generates a markdown-formatted report from JSON research data.
- **Implementation**:
  - Uses a `PromptTemplate` to instruct Llama3 (`llama3-70b-8192`) to identify themes, clusters, and gaps.
  - Formats output as markdown with sections: `Inferred Topic`, `Cluster 1`, `Common terms`, `Research Gaps`.
  - Handles errors by returning an error string.
- **Purpose**: Provides a structured analysis for downstream topic suggestion.

### 3. Fallback Topic Generation (`InnovationAgent`)
- **Description**: A rule-based algorithm to generate 3-5 research topics if the Groq API fails.
- **Implementation**:
  - Parses the `analysis_report` using regex to extract `topic`, `cluster_terms`, and `gaps`.
  - Generates topics by combining gaps and terms (e.g., `Developing {gap} techniques to enhance {term} in {topic} systems`).
  - Adds generic topics if insufficient gaps/terms (e.g., `Pioneering {topic} integration with emerging AI and IoT technologies`).
  - Ensures 3-5 topics are always returned, formatted as markdown.
- **Purpose**: Ensures robustness against API failures, maintaining system functionality.

## Innovations
1. **Hybrid Data Processing**:
   - Combines external data retrieval (Arxiv API) with advanced LLM inference (Groq’s Llama3) in a single workflow, enabling real-world data-driven research insights.
2. **Lightweight Storage**:
   - Uses `st.session_state` for temporary result storage, eliminating the need for a database and simplifying deployment.
3. **User-Friendly Interface**:
   - Streamlit’s interactive UI with a pandas DataFrame for Arxiv results and markdown rendering for analysis/topics provides an intuitive experience.
4. **Modular Agent Design**:
   - Each agent (`Research`, `Analysis`, `Innovation`) is independent, allowing easy replacement or enhancement (e.g., swapping Arxiv for another data source).

## Limitations
1. **Groq API Dependency**:
   - Relies on the Groq API for `AnalysisAgent` and `InnovationAgent`, introducing latency and potential rate limits.
   - API errors (e.g., model unavailability) trigger fallbacks, which may produce less sophisticated results.
2. **Arxiv API Constraints**:
   - Limited to 3 papers with summaries truncated at 50,000 characters, potentially missing comprehensive data.
   - Arxiv’s coverage may exclude relevant non-Arxiv sources.
3. **Session State Volatility**:
   - Results in `st.session_state` are lost when the Streamlit session ends, lacking persistence.
4. **Async Handling in Streamlit**:
   - Uses `asyncio.run` for async calls, which may block the main thread. Threading or async frameworks (e.g., FastAPI) would improve performance.
5. **Error Handling**:
   - Basic error display via `st.error` and fallback warnings. Lacks retry logic or detailed diagnostics.

## Future Work
1. **Enhanced Data Sources**:
   - Integrate additional APIs (e.g., PubMed, Google Scholar) to broaden research coverage.
   - Allow users to select data sources via the UI.
2. **Persistent Storage**:
   - Add optional database support (e.g., SQLite) for result persistence, configurable via the UI.
3. **Improved Error Handling**:
   - Implement retry logic for API failures and provide detailed error diagnostics.
   - Add user-facing retry buttons in the Streamlit app.
4. **Performance Optimization**:
   - Cache Arxiv results using `st.cache_data` to reduce API calls.
   - Use threading or an async web framework (e.g., FastAPI) for better async handling.
5. **Advanced UI Features**:
   - Add export options (e.g., CSV, PDF) for results.
   - Implement query history filtering and pagination for large result sets.
   - Enhance visualization with charts for clusters or topic trends.
6. **Model Flexibility**:
   - Allow users to select alternative Groq models (e.g., `llama3-8b-8192`) or local models via Ollama for offline use.
7. **Authentication and Security**:
   - Add user authentication to secure query history and results.
   - Encrypt sensitive data (e.g., queries) if stored persistently.

## Conclusion
The Multi-Agent Research System provides a robust, lightweight solution for academic research, integrating Arxiv data with Llama3-powered analysis and topic suggestion. Its LangGraph-orchestrated workflow, modular agent design, and Streamlit interface make it accessible and extensible. While limited by API dependencies and session state volatility, future enhancements can address these by adding data sources, persistence, and advanced UI features.