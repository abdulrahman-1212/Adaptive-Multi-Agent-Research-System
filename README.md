# Multi-Agent Research System
**Streamlit App**: https://adaptive-multi-agent-research-system-ahkkgufrvkx9ycdacmwmxh.streamlit.app/
This project is a Streamlit-based web application that implements a Multi-Agent System (MAS) for academic research. It uses LangGraph to orchestrate three agents: `ResearchAgent` for fetching papers from Arxiv, `AnalysisAgent` for analyzing research data, and `InnovationAgent` for suggesting novel research topics. The system leverages the Groq API with the Llama3 model (`llama3-70b-8192`) for inference and stores results in Streamlit's session state, requiring no database.

## Features
- **Arxiv Search**: Fetches up to three research papers from Arxiv using a user-provided query.
- **Analysis**: Identifies themes, clusters, and gaps in the fetched papers using Llama3 via Groq.
- **Innovation**: Proposes 3-5 innovative research topics based on the analysis, with a rule-based fallback if the Groq API fails.
- **Interactive UI**: A Streamlit interface allows users to submit queries, view results in a table and markdown format, and clear session state.
- **No Database**: Results are stored temporarily in `st.session_state`, ensuring lightweight operation.

## Project Structure
```
project/
├── agents/
│   ├── research_agent.py    # Fetches papers from Arxiv
│   ├── analysis_agent.py   # Analyzes research data
│   ├── innovation_agent.py # Suggests innovative topics
│   ├── research_mas.py     # Orchestrates MAS with LangGraph
├── app.py                  # Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (Grok API key)
```

## Prerequisites
- Python 3.8+
- A Groq API key
- Internet access for Arxiv and Groq API calls

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd multi-agent-research-system
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following content:
   ```
   GROK_API_KEY=<your-grok-api-key>
   ```
   Replace `<your-grok-api-key>` with your actual Groq API key.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   The `requirements.txt` includes:
   ```
   streamlit==1.39.0
   langchain-groq==0.2.0
   langgraph==0.2.34
   python-dotenv==1.0.1
   langchain-community==0.3.1
   ```

## Usage
1. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`.

2. **Interact with the App**:
   - **Enter a Query**: Input a research topic (e.g., "AI in healthcare") in the text field.
   - **Submit Query**: Click the "Submit Query" button to run the MAS workflow.
   - **View Results**:
     - **Research Papers**: Displayed in a table with titles and summaries from Arxiv.
     - **Analysis Report**: Markdown-formatted report identifying themes, clusters, and gaps.
     - **Suggested Topics**: Markdown-formatted list of 3-5 innovative research topics.
   - **Clear Results**: Click the "Clear Results" button to reset the session state.

3. **Example Query**:
   - Input: `AI in healthcare`
   - Output:
     - **Research Papers**: A table with up to three Arxiv papers (title and summary).
     - **Analysis Report**: E.g., `**Inferred Topic**: AI in Healthcare\n### Cluster 1\n**Common terms**: machine learning, diagnostics\n## Research Gaps\n- Limited real-world deployment\n- Ethical considerations`
     - **Suggested Topics**: E.g., `# Suggested Research Topics\n**Based on Topic**: AI in Healthcare\n## Proposed Topics\n1. Developing ethical frameworks for AI diagnostics\n2. Enhancing real-world deployment of machine learning in healthcare\n3. Integrating AI with wearable health devices`

## Implementation Details
- **Agents**:
  - **ResearchAgent**: Uses `langchain_community.utilities.arxiv.ArxivAPIWrapper` to fetch up to three Arxiv papers, parsed into JSON with `title` and `summary` fields.
  - **AnalysisAgent**: Uses `langchain_groq.ChatGroq` with `llama3-70b-8192` to analyze Arxiv results, producing a markdown report with themes, clusters, and gaps.
  - **InnovationAgent**: Uses `langchain_groq.ChatGroq` with `llama3-70b-8192` to suggest 3-5 research topics.
- **Workflow**: LangGraph orchestrates the agents in a sequential workflow: `ResearchAgent` → `AnalysisAgent` → `InnovationAgent`.
- **Storage**: Results are stored in `st.session_state.results`, cleared via the "Clear Results" button.
- **Error Handling**: Displays errors for Arxiv or Groq API failures and warns if the fallback mechanism is used.
- 
## Example
**Input**: Physics Informed Neural Network.
**Output**:
   **Research Papers**: 
      1. Revisiting PINNs: Generative Adversarial Physics-informed Neural Networks and Point-weighting Method.
      2. From short-sighted to far-sighted: A comparative study of recursive machine learning approaches for open quantum systems.
      3. Auto-PINN: Understanding and Optimizing Physics-Informed Neural Architecture.
   **Research Gaps**:
      1. Lack of comparative studies: Only one paper is conducting a comparative study of recursive machine learning approaches for open quantum systems, indicating a potential gap in the literature for more comprehensive comparisons.
      2. Optimization and understanding of PINNs: While one paper is focused on understanding and optimizing PINNs, there may be a need for further research in this area to fully unlock the potential of PINNs in scientific applications.
   **Suggested Research Topics**:
      1. Comparative Analysis of PINNs and Recursive Machine Learning Approaches for Quantum Many-Body Systems
      2. Optimization of PINNs for Noisy Quantum Systems: A Bayesian Approach.
      3. Physics-Constrained Neural Networks for Quantum Information Processing: A Hybrid Approach.
      4. PINNs for Quantum Error Correction: A Machine Learning Perspective.
      5. Interpretable PINNs for Quantum Systems: Unveiling Physical Insights.
      
## Notes
- **Model Choice**: Uses `llama3-70b-8192` via Groq, as `llama2-70b-4096` is not supported. Ensure the Groq API key has access to this model.
- **Arxiv Limits**: Fetches up to 3 papers with summaries truncated at 50,000 characters. Adjust `top_k_results` or `doc_content_chars_max` in `research_agent.py` if needed.
- **Async Handling**: Uses `asyncio.run` for async LangGraph nodes in Streamlit. For production, consider threading for better async support.
- **Security**: Keep the `.env` file secure and exclude it from version control (e.g., add to `.gitignore`).
- **Performance**: The `llama3-70b-8192` model may have latency via Groq. Test with smaller queries to optimize.
- **Enhancements**: Consider adding:
  - Export options (e.g., CSV download for results).
  - Query history filtering.
  - Retry logic for API failures.
  - Advanced UI features (e.g., pagination for results).

## Troubleshooting
- **Groq API Error**: If you see `Error code: 404 - {'error': {'message': 'The model does not exist...'}}`, verify the model name (`llama3-70b-8192`) and API key in `.env`.
- **Arxiv Search Failure**: Check internet connectivity or adjust `ARXIV_MAX_QUERY_LENGTH` in `research_agent.py`.
- **Slow Performance**: Reduce `doc_content_chars_max` in `research_agent.py` or test with simpler queries.
- **Session State Issues**: Use the "Clear Results" button to reset if results accumulate unexpectedly.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Built with [Streamlit](https://streamlit.io), [LangGraph](https://github.com/langchain-ai/langgraph), [langchain-groq](https://github.com/langchain-ai/langchain), and [langchain-community](https://github.com/langchain-ai/langchain).
- Powered by Groq's Llama3-70b-8192 model and Arxiv API.
