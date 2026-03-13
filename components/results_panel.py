import streamlit as st
from core.refiner import RefinementResult

CHANGE_CONFIG = {
    "removed":      {"emoji": "🗑️", "color": "#FCEBEB", "label": "Removed"},
    "clarified":    {"emoji": "✏️",  "color": "#FAEEDA", "label": "Clarified"},
    "restructured": {"emoji": "🔀", "color": "#E6F1FB", "label": "Restructured"},
    "added":        {"emoji": "➕", "color": "#EAF3DE", "label": "Added"},
}


def _score_color(score: int) -> str:
    if score <= 3:
        return "🔴"
    elif score <= 6:
        return "🟡"
    return "🟢"


def render_results(result: RefinementResult) -> None:
    """Renders the full refinement result: metrics, refined prompt, and change log."""

    # ── Top metrics row ──────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quality score (original)", f"{_score_color(result.quality_score)} {result.quality_score} / 10")
    with col2:
        original_words = len(result.raw_input.split())
        refined_words = len(result.refined_prompt.split())
        delta = refined_words - original_words
        st.metric("Word count", refined_words, delta=f"{delta:+d} vs original")
    with col3:
        st.metric("Changes made", len(result.changes))

    st.divider()

    # ── Intent summary ───────────────────────────────────────────────
    st.info(f"**Detected intent:** {result.intent_summary}")

    # ── Refined prompt ───────────────────────────────────────────────
    st.markdown("### ✅ Refined prompt")
    st.code(result.refined_prompt, language=None, wrap_lines=True)

    col_copy, _ = st.columns([1, 3])
    with col_copy:
        if st.button("📋 Copy to clipboard", key="copy_btn"):
            st.write(
                f'<script>navigator.clipboard.writeText({repr(result.refined_prompt)})</script>',
                unsafe_allow_html=True,
            )
            st.toast("Copied!", icon="✅")

    # ── Change log ───────────────────────────────────────────────────
    if result.changes:
        st.markdown("### 📋 Change log")
        for change in result.changes:
            cfg = CHANGE_CONFIG.get(change.type, CHANGE_CONFIG["clarified"])
            st.markdown(
                f"""<div style="
                    background:{cfg['color']};
                    border-radius:8px;
                    padding:10px 14px;
                    margin-bottom:8px;
                    font-size:14px;
                    font-family:sans-serif;
                    color:#333;
                ">
                <b>{cfg['emoji']} {cfg['label']}</b> &nbsp;—&nbsp; {change.description}
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Side-by-side diff ────────────────────────────────────────────
    with st.expander("🔍 Before / After comparison"):
        left, right = st.columns(2)

        # raw_input may be empty if result was loaded from history,
        # fall back to whatever is currently in the input widget
        raw = result.raw_input or st.session_state.get("raw_prompt_input", "")

        with left:
            st.markdown("**Original**")
            st.text_area(
                label="original_text",
                label_visibility="collapsed",
                value=raw,
                height=180,
                disabled=True,
                key="diff_original",
            )
        with right:
            st.markdown("**Refined ✅**")
            st.text_area(
                label="refined_text",
                label_visibility="collapsed",
                value=result.refined_prompt,
                height=180,
                disabled=True,
                key="diff_refined",
            )