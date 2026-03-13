import os
import streamlit as st

from core.refiner import PromptRefiner
from utils.history import HistoryManager
from components.input_panel import render_input_panel
from components.results_panel import render_results
from components.sidebar import render_sidebar

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prompt Refiner",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = HistoryManager()
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("ANTHROPIC_API_KEY", "")
if "model" not in st.session_state:
    st.session_state.model = "claude-sonnet-4-20250514"
if "loaded_result" not in st.session_state:
    st.session_state.loaded_result = None

history: HistoryManager = st.session_state.history

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar(history)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("✨ Prompt Refiner")
st.markdown(
    "Strip noise. Clarify intent. Get better outputs from any LLM.",
)
st.divider()

# ── Main layout ───────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    prompt, submitted = render_input_panel()

    if submitted:
        api_key = st.session_state.get("api_key", "")
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("Refining your prompt..."):
                try:
                    refiner = PromptRefiner(
                        api_key=api_key,
                        model=st.session_state.get("model", "claude-sonnet-4-20250514"),
                    )
                    result = refiner.refine(prompt)
                    history.add(result)
                    st.session_state.loaded_result = result
                except ValueError as e:
                    st.error(f"Validation error: {e}")
                except Exception as e:
                    st.error(f"API error: {e}")

with right_col:
    result = st.session_state.get("loaded_result")
    if result:
        render_results(result)
    else:
        st.markdown(
            """
            <div style="
                border: 2px dashed #ddd;
                border-radius: 12px;
                padding: 3rem 2rem;
                text-align: center;
                color: #aaa;
                font-family: sans-serif;
            ">
                <div style="font-size: 48px; margin-bottom: 1rem;">✨</div>
                <div style="font-size: 16px;">Your refined prompt will appear here</div>
                <div style="font-size: 13px; margin-top: 8px;">Type a prompt on the left and hit Refine</div>
            </div>
            """,
            unsafe_allow_html=True,
        )