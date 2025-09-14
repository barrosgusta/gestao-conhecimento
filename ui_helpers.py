# ui_helpers.py
from typing import Callable, Sequence, Any

import streamlit as st

CSS_INJECTED_KEY = "_custom_css_injected"

CUSTOM_CSS = """
<style>
/* General font tweaks */
html, body, [class^=block-container] {font-family: 'Inter', system-ui, sans-serif;}

/* Colored labels for selectboxes */
div.row-widget.stSelectbox label {color:#1b4d91; font-weight:600;}

/* Tooltip container */
.tooltip-wrapper {display:flex; align-items:center; gap:.4rem;}
.tooltip-container {position: relative; display: inline-block; cursor: help; font-size:0.95rem;}
.tooltip-container .tooltip-icon {background:#1b4d91; color:#fff; border-radius:50%; width:18px; height:18px; display:flex; align-items:center; justify-content:center; font-size:12px; line-height:1;}
.tooltip-container .tooltip-text {visibility:hidden; opacity:0; transition:opacity .25s; position:absolute; z-index:10; top:125%; left:50%; transform:translateX(-50%); background:#1b1f27; color:#fff; padding:.55rem .7rem; border-radius:6px; width:240px; font-size:.70rem; text-align:left; box-shadow:0 4px 14px rgba(0,0,0,.25);} 
.tooltip-container:hover .tooltip-text {visibility:visible; opacity:1;}
</style>
"""


def ensure_css():
    if not st.session_state.get(CSS_INJECTED_KEY):
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        st.session_state[CSS_INJECTED_KEY] = True


def select_with_tooltip(label: str,
                        options: Sequence[Any],
                        key: str,
                        get_description: Callable[[Any], str]):
    """Render a selectbox with an info (tooltip) icon to the right.

    Returns selected option.
    """
    ensure_css()
    col_sel, col_tip = st.columns([14, 1])
    selected = col_sel.selectbox(label, options=options, key=key)
    desc = (get_description(selected) or "Descrição não disponível.").replace('<', '&lt;').replace('>', '&gt;')
    col_tip.markdown(
        f"""
        <div class='tooltip-container'>
            <div class='tooltip-icon'>i</div>
            <div class='tooltip-text'>{desc}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return selected
