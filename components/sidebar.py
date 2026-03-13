import streamlit as st
from utils.history import HistoryManager
from core.refiner import GROQ_MODELS


def render_sidebar(history: HistoryManager) -> None:
    """Renders the sidebar with API key input, model selector, and history."""

    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        # API key
        st.markdown(
            "Get a free key at [console.groq.com](https://console.groq.com)",
            unsafe_allow_html=True,
        )
        api_key = st.text_input(
            "Groq API key",
            type="password",
            placeholder="gsk_...",
            help="Free tier — no credit card needed.",
            key="api_key_input",
        )
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("API key set", icon="🔑")

        # Model selector
        model = st.selectbox(
            "Model",
            options=GROQ_MODELS,
            index=0,
            key="model_select",
            help="llama-3.3-70b is the best quality. llama-3.1-8b-instant is fastest.",
        )
        st.session_state["model"] = model

        st.divider()

        # History
        st.markdown("## 🕐 History")

        if len(history) == 0:
            st.caption("No refinements yet.")
            return

        if st.button("🗑 Clear history", use_container_width=True):
            history.clear()
            st.rerun()

        for i, entry in enumerate(history.get_all()):
            score = entry.result.quality_score
            icon = "🔴" if score <= 3 else "🟡" if score <= 6 else "🟢"
            if st.button(
                f"{icon} {entry.label}",
                key=f"history_{i}",
                use_container_width=True,
            ):
                st.session_state["loaded_result"] = entry.result
                st.rerun()