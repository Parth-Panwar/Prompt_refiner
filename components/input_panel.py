import streamlit as st


def render_input_panel() -> tuple[str, bool]:
    """
    Renders the raw prompt input area.
    Returns (prompt_text, submitted).
    """
    st.markdown("### Your raw prompt")
    st.caption("Type anything — messy, informal, full of assumptions. We'll clean it up.")

    prompt = st.text_area(
        label="Raw prompt",
        label_visibility="collapsed",
        placeholder="e.g. hey so i wanna build like a todo app in react idk maybe with drag and drop or something, can u write the code for me",
        height=150,
        key="raw_prompt_input",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if prompt:
            st.caption(f"{len(prompt)} characters · {len(prompt.split())} words")
    with col2:
        submitted = st.button("Refine →", type="primary", use_container_width=True, disabled=not prompt.strip())

    return prompt, submitted