import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from functools import lru_cache

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WE LOVE — ManyChat Analytics",
    page_icon="♡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
BASE = {
    "bg":        "#060608",
    "surface":   "#0C0C12",
    "surface2":  "#111118",
    "surface3":  "#16161F",
    "text":      "#DDD8E4",
    "muted":     "#6B6478",
    "mid":       "#9C94AA",
    "white":     "#F5F2F8",
}

THEMES = {
    "rose": {
        "accent":     "#D63655",
        "accent_lt":  "#F05070",
        "accent_dim": "rgba(214,54,85,0.08)",
        "border":     "rgba(214,54,85,0.14)",
        "border_hi":  "rgba(214,54,85,0.40)",
    },
    "red": {
        "accent":     "#CC1A1A",
        "accent_lt":  "#E83535",
        "accent_dim": "rgba(204,26,26,0.08)",
        "border":     "rgba(204,26,26,0.14)",
        "border_hi":  "rgba(204,26,26,0.40)",
    },
    "green": {
        "accent":     "#1F7A4A",
        "accent_lt":  "#2EA660",
        "accent_dim": "rgba(31,122,74,0.08)",
        "border":     "rgba(31,122,74,0.14)",
        "border_hi":  "rgba(31,122,74,0.40)",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  CAMPAIGN DEFINITIONS — single source of truth
# ─────────────────────────────────────────────────────────────────────────────
CAMPANHAS = {
    "Todas as Campanhas": {
        "emoji":        "◈",
        "desc":         "Visão consolidada de todas as automações ManyChat ativas.",
        "cols":         None,
        "etapas":       None,
        "label_resumo": None,
        "kpi_sub_col":  None,
        "kpi_sub_label": None,
        "kpi_note":     None,
    },
    "Acesso Comercial": {
        "emoji":        "◆",
        "desc":         "Automação de entrada pelo fluxo comercial direto.",
        "cols": [
            "Comercial (Iniciou)",
            "Comercial (clicou em quero saber mais)",
            "Comercial (Clicou Wpp)",
        ],
        "etapas":       ["Iniciou", "Quero Saber Mais", "Clicou no Wpp"],
        "label_resumo": "Acesso Comercial",
        "kpi_sub_col":  "Comercial (Clicou Wpp)",
        "kpi_sub_label": "→ Wpp",
        "kpi_note":     "Fluxo comercial direto",
    },
    "Campanha Comunidade": {
        "emoji":        "◈",
        "desc":         "Automação de leads da campanha da comunidade.",
        "cols": [
            "Campanha Comunidade (Iniciou)",
            "Campanha Comunidade (clicou em quero saber mais)",
            "Campanha Comunidade (Clicou Wpp)",
        ],
        "etapas":       ["Iniciou", "Quero Saber Mais", "Clicou no Wpp"],
        "label_resumo": "Comunidade",
        "kpi_sub_col":  "Campanha Comunidade (Clicou Wpp)",
        "kpi_sub_label": "→ Wpp",
        "kpi_note":     "Campanha da comunidade",
    },
    "We Love Rental – Comunidade": {
        "emoji":        "◇",
        "desc":         "Automação do fluxo de aluguel da comunidade We Love.",
        "cols": [
            "We Love Rental - Comunidade (Iniciou)",
            "We Love Rental - Comunidade (Acessou site)",
        ],
        "etapas":       ["Iniciou", "Acessou o Site"],
        "label_resumo": "WL Rental",
        "kpi_sub_col":  "We Love Rental - Comunidade (Acessou site)",
        "kpi_sub_label": "→ Site",
        "kpi_note":     "Fluxo de aluguel",
    },
    "Caderno Secreto": {
        "emoji":        "▣",
        "desc":         "Automação de leads captados pelo Caderno Secreto.",
        "cols": [
            "Caderno Secreto (Iniciou)",
            "Caderno Secreto (clicou em saber mais)",
            "Caderno Secreto (Mandou wpp)",
            "Caderno Secreto (Acessou)",
            "Caderno Secreto (Clicou Wpp)",
        ],
        "etapas":       ["Iniciou", "Saber Mais", "Mandou Wpp", "Acessou", "Clicou Wpp"],
        "label_resumo": "Caderno Secreto",
        "kpi_sub_col":  "Caderno Secreto (Clicou Wpp)",
        "kpi_sub_label": "→ Wpp",
        "kpi_note":     "Caderno Secreto",
    },
}

ALL_REQUIRED_COLS = [
    col
    for info in CAMPANHAS.values()
    if info["cols"] is not None
    for col in info["cols"]
]

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  editorial luxury terminal
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {{
  --bg:       {BASE['bg']};
  --surface:  {BASE['surface']};
  --surface2: {BASE['surface2']};
  --surface3: {BASE['surface3']};
  --text:     {BASE['text']};
  --muted:    {BASE['muted']};
  --mid:      {BASE['mid']};
  --white:    {BASE['white']};
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"] {{
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}}

/* Noise texture overlay */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    background-size: 180px;
    opacity: 0.6;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}

[data-testid="block-container"] {{ padding: 0 !important; max-width: 100% !important; }}

/* ── Tabs ── */
[data-testid="stTabs"] > div:first-child {{
    background: var(--bg) !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    padding: 0 2.5rem !important;
    gap: 0 !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 400 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid transparent !important;
    padding: 1rem 1.4rem !important;
    transition: color .2s, border-color .2s !important;
}}
button[data-baseweb="tab"]:hover {{ color: var(--mid) !important; }}
button[aria-selected="true"][data-baseweb="tab"] {{
    color: var(--white) !important;
    border-bottom: 1px solid var(--white) !important;
    background: transparent !important;
}}
[data-testid="stTabsContent"] {{ padding: 0 !important; background: transparent !important; }}

/* ── Buttons ── */
.stButton > button {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem !important;
    font-weight: 400 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--mid) !important;
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 3px !important;
    padding: 0.4rem 1rem !important;
    transition: all .2s !important;
}}
.stButton > button:hover {{
    color: var(--white) !important;
    border-color: rgba(255,255,255,0.25) !important;
    background: rgba(255,255,255,0.03) !important;
}}

/* ── Plotly ── */
.js-plotly-plot, .plotly, .stPlotlyChart > div {{ background: transparent !important; }}
[data-testid="column"] > div:first-child {{ padding: 0 !important; }}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {{ display: none !important; }}
[data-testid="stSelectbox"] > div > div {{
    background: var(--surface2) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 4px !important;
    color: var(--white) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
}}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {{ border-top-color: var(--mid) !important; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    background: var(--surface2) !important;
    border-radius: 4px !important;
    font-family: 'Syne', sans-serif !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────────────────────────────
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1QZ6TJhikHTwhJDsbxQpA88GPj-QUFclHfUVFQVsPtsU"
    "/export?format=csv&gid=0"
)

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map({"TRUE": True, "FALSE": False, True: True, False: False})
    bool_cols = [c for c in df.columns if set(df[c].dropna().unique()).issubset({True, False})]
    return df[bool_cols]

def validate_columns(df):
    return [c for c in ALL_REQUIRED_COLS if c not in df.columns]

def build_metrics(df):
    return {col: int(df[col].sum()) for col in df.columns}

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=64)
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def pct(total, part):
    return round(part / total * 100, 1) if total else None

def fmt_pct(total, part):
    v = pct(total, part)
    return f"{v:.1f}%" if v is not None else "—"

def safe_pct(total, part):
    v = pct(total, part)
    return v if v is not None else 0.0

def base_layout(**kw):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Syne", color=BASE["mid"], size=11),
        margin=dict(l=4, r=4, t=20, b=4),
        **kw,
    )

# ─────────────────────────────────────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def chart_funnel(labels, values, title, T):
    n = len(labels)
    ar, ag, ab = hex_rgb(T["accent"])
    alphas = [round(1.0 - i * (0.52 / max(n - 1, 1)), 2) for i in range(n)]
    colors = [f"rgba({ar},{ag},{ab},{a})" for a in alphas]
    height = max(200, min(480, n * 76))
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textposition="inside",
        texttemplate="<b>%{value:,}</b><br><span style='font-size:9px;opacity:.6'>%{percentInitial:.0%}</span>",
        textfont=dict(color=BASE["white"], family="Syne", size=11),
        connector=dict(
            fillcolor=BASE["surface"],
            line=dict(color=f"rgba({ar},{ag},{ab},0.12)", width=1),
        ),
        marker=dict(
            color=colors,
            line=dict(color=f"rgba({ar},{ag},{ab},0.2)", width=1),
        ),
    ))
    fig.update_layout(
        **base_layout(height=height),
        title=dict(
            text=title,
            font=dict(family="JetBrains Mono", size=8, color=BASE["muted"]),
            x=0.5, y=0.99,
        ),
    )
    return fig

def chart_bar_h(labels, values, T):
    ar, ag, ab = hex_rgb(T["accent"])
    mx = max(values) if values else 1
    colors = [f"rgba({ar},{ag},{ab},{round(0.25 + 0.75*(v/mx), 2)})" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, cornerradius=3, line=dict(width=0)),
        text=[f"<b>{v:,}</b>" for v in values],
        textposition="outside",
        textfont=dict(color=BASE["mid"], family="Syne", size=11),
    ))
    fig.update_layout(
        **base_layout(height=max(180, len(labels) * 50)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, mx * 1.25]),
        yaxis=dict(showgrid=False, tickfont=dict(family="Syne", size=11, color=BASE["mid"])),
    )
    return fig

def chart_donut(labels, values, T):
    ar, ag, ab = hex_rgb(T["accent"])
    n = len(labels)
    colors = [f"rgba({ar},{ag},{ab},{round(1.0 - i * 0.17, 2)})" for i in range(n)]
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=colors, line=dict(color=BASE["bg"], width=3)),
        textfont=dict(color=BASE["mid"], family="Syne", size=10),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:,} contatos — %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **base_layout(height=240),
        showlegend=True,
        legend=dict(
            font=dict(family="Syne", size=10, color=BASE["mid"]),
            bgcolor="rgba(0,0,0,0)", x=1.0, y=0.5,
        ),
        annotations=[dict(
            text=f"<b>{total:,}</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=BASE["white"], family="Bebas Neue", size=28),
        )],
    )
    return fig

def chart_conv_bars(stages, rates, T):
    ar, ag, ab = hex_rgb(T["accent"])
    safe = [r if r is not None else 0.0 for r in rates]
    mx = max(safe) if safe else 1
    colors = [
        f"rgba({ar},{ag},{ab},{round(0.2 + 0.8*(r/max(mx,1)), 2)})" if r
        else f"rgba({ar},{ag},{ab},0.1)"
        for r in safe
    ]
    texts = [f"<b>{r:.1f}%</b>" if r else "—" for r in safe]
    fig = go.Figure(go.Bar(
        x=safe, y=stages, orientation="h",
        marker=dict(color=colors, cornerradius=3, line=dict(width=0)),
        text=texts, textposition="outside",
        textfont=dict(color=BASE["mid"], family="Syne", size=11),
    ))
    fig.update_layout(
        **base_layout(height=max(200, len(stages) * 44)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 125]),
        yaxis=dict(showgrid=False, tickfont=dict(family="Syne", size=10.5, color=BASE["mid"])),
    )
    return fig

def chart_table(rows, T):
    ar, ag, ab = hex_rgb(T["accent"])
    row_fill = [BASE["surface"] if i % 2 == 0 else BASE["surface2"] for i in range(len(rows))]
    fig = go.Figure(go.Table(
        columnwidth=[380, 110, 100],
        header=dict(
            values=["<b>ETAPA / AUTOMAÇÃO MANYCHAT</b>", "<b>CONTATOS</b>", "<b>% TOTAL</b>"],
            fill_color=BASE["surface3"],
            font=dict(color=f"rgba({ar},{ag},{ab},0.85)", family="JetBrains Mono", size=9),
            align=["left", "center", "center"],
            height=36,
            line_color=T["border"],
        ),
        cells=dict(
            values=[[r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]],
            fill_color=[row_fill],
            font=dict(
                color=[BASE["text"], BASE["white"], BASE["mid"]],
                family="Syne", size=11,
            ),
            align=["left", "center", "center"],
            height=32,
            line_color=T["border"],
        ),
    ))
    fig.update_layout(**base_layout(height=len(rows) * 32 + 50))
    return fig

# ─────────────────────────────────────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def ui_topbar(title, subtitle, T, tab_key):
    """Full-width topbar with ManyChat badge. Returns True if sync clicked."""
    ar, ag, ab = hex_rgb(T["accent"])

    clicked = False
    col_main, col_btn = st.columns([10, 1])

    with col_main:
        st.markdown(f"""
        <div style="padding: 2.6rem 2.5rem 0;">

          <!-- ManyChat badge -->
          <div style="display:inline-flex;align-items:center;gap:0.5rem;
                      background:rgba({ar},{ag},{ab},0.10);
                      border:1px solid rgba({ar},{ag},{ab},0.30);
                      border-radius:3px;
                      padding:0.28rem 0.75rem 0.28rem 0.55rem;
                      margin-bottom:1.1rem;">
            <svg width="14" height="14" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="6" fill="rgba({ar},{ag},{ab},0.7)"/>
              <path d="M7 23V11l9 8 9-8v12" stroke="white" stroke-width="2.8"
                    stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;
                         font-weight:500;letter-spacing:2.5px;text-transform:uppercase;
                         color:{T['accent_lt']};">ManyChat Automations</span>
          </div>

          <!-- Title -->
          <div style="display:flex;align-items:flex-end;gap:1.2rem;flex-wrap:wrap;">
            <h1 style="font-family:'Bebas Neue',sans-serif;
                       font-size:clamp(2.8rem,5vw,4.4rem);
                       font-weight:400;letter-spacing:1.5px;
                       color:{BASE['white']};line-height:0.92;
                       text-transform:uppercase;">
              {title}
            </h1>
            <span style="font-family:'Syne',sans-serif;font-size:0.78rem;
                         color:{BASE['mid']};font-weight:500;
                         margin-bottom:0.35rem;letter-spacing:0.3px;">
              {subtitle}
            </span>
          </div>

          <!-- Accent rule -->
          <div style="margin-top:1.6rem;height:1px;
               background:linear-gradient(90deg,
                 rgba({ar},{ag},{ab},0.55) 0%,
                 rgba({ar},{ag},{ab},0.12) 45%,
                 transparent 100%);"></div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown('<div style="padding-top:3.2rem;padding-right:1rem;">', unsafe_allow_html=True)
        if st.button("↺ sync", key=f"sync_{tab_key}"):
            clicked = True
        st.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:0.45rem;'
            f'color:{BASE["muted"]};text-align:right;margin-top:0.3rem;letter-spacing:1px;'
            f'text-transform:uppercase;">auto 5m</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    return clicked


def ui_section_label(text, T, margin_top="2.4rem"):
    ar, ag, ab = hex_rgb(T["accent"])
    st.markdown(f"""
    <div style="padding: 0 2.5rem; margin-top:{margin_top}; margin-bottom:0.7rem;
                display:flex; align-items:center; gap:0.6rem;">
      <div style="width:18px;height:1px;background:rgba({ar},{ag},{ab},0.5);flex-shrink:0;"></div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.52rem;font-weight:500;
                   letter-spacing:3px;text-transform:uppercase;color:{T['accent']};
                   opacity:0.8;">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def ui_thin_divider(T):
    ar, ag, ab = hex_rgb(T["accent"])
    st.markdown(
        f'<div style="height:1px;margin:0.6rem 2.5rem 0;'
        f'background:linear-gradient(90deg,transparent,'
        f'rgba({ar},{ag},{ab},0.15),transparent);"></div>',
        unsafe_allow_html=True,
    )


def ui_kpi_row(items, T):
    ar, ag, ab = hex_rgb(T["accent"])

    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        cols = st.columns(len(items))
        for col, item in zip(cols, items):
            is_total     = item.get("is_total", False)
            border_color = T["border_hi"] if is_total else T["border"]
            top_bar      = f"rgba({ar},{ag},{ab},0.8)" if is_total else f"rgba({ar},{ag},{ab},0.4)"
            label_color  = T["accent_lt"] if is_total else BASE["muted"]
            sub_color    = T["accent_lt"]

            sub_h = (
                f'<div style="font-family:Syne,sans-serif;font-size:0.7rem;font-weight:600;'
                f'color:{sub_color};margin-top:0.4rem;">{item["sub"]}</div>'
            ) if item.get("sub") else ""
            note_h = (
                f'<div style="font-family:JetBrains Mono,monospace;font-size:0.55rem;'
                f'color:{BASE["mid"]};margin-top:0.35rem;letter-spacing:0.5px;'
                f'opacity:0.85;">{item["note"]}</div>'
            ) if item.get("note") else ""

            ghost = item["value"].replace(",", "").replace("%", "")

            col.markdown(f"""
            <div style="
              background:{BASE['surface']};
              border:1px solid {border_color};
              border-radius:6px;
              padding:1.4rem 1.5rem 1.3rem;
              position:relative;overflow:hidden;
              min-height:138px;
            ">
              <div style="position:absolute;top:0;left:0;right:0;height:2px;
                          background:{top_bar};"></div>
              <div style="position:absolute;bottom:-20px;right:-8px;
                          font-family:'Bebas Neue',sans-serif;
                          font-size:5.5rem;line-height:1;
                          color:rgba(255,255,255,0.018);
                          pointer-events:none;user-select:none;letter-spacing:2px;">
                {ghost}
              </div>
              <div style="font-family:'Bebas Neue',sans-serif;
                          font-size:2.9rem;font-weight:400;
                          color:{BASE['white']};line-height:1;letter-spacing:1px;">
                {item['value']}
              </div>
              <div style="font-family:'Syne',sans-serif;font-size:0.62rem;font-weight:700;
                          letter-spacing:2px;text-transform:uppercase;
                          color:{label_color};margin-top:0.5rem;">
                {item['label']}
              </div>
              {sub_h}
              {note_h}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def ui_insight_strip(cards, T):
    """Compact horizontal insight cards — one per column."""
    ar, ag, ab = hex_rgb(T["accent"])
    cols = st.columns(len(cards))
    for col, (icon, tag, value, sub) in zip(cols, cards):
        sub_h = (
            f'<div style="font-size:0.65rem;color:{BASE["mid"]};'
            f'margin-top:0.2rem;font-family:Syne,sans-serif;line-height:1.5;">{sub}</div>'
        ) if sub else ""
        col.markdown(f"""
        <div style="background:{BASE['surface']};border:1px solid {T['border']};
                    border-radius:6px;padding:0.9rem 1rem;
                    display:flex;gap:0.65rem;align-items:flex-start;">
          <span style="font-size:1rem;margin-top:0.05rem;flex-shrink:0;">{icon}</span>
          <div>
            <div style="font-family:JetBrains Mono,monospace;font-size:0.47rem;font-weight:500;
                        letter-spacing:2.5px;text-transform:uppercase;
                        color:{T['accent_lt']};margin-bottom:0.2rem;">{tag}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;
                        color:{BASE['white']};line-height:1.1;letter-spacing:0.5px;">{value}</div>
            {sub_h}
          </div>
        </div>
        """, unsafe_allow_html=True)


def ui_info_box(icon, title, body, T):
    ar, ag, ab = hex_rgb(T["accent"])
    st.markdown(f"""
    <div style="margin:0 2.5rem 1rem;padding:0.85rem 1.1rem;
                background:rgba({ar},{ag},{ab},0.04);
                border:1px solid rgba({ar},{ag},{ab},0.12);
                border-left:2px solid rgba({ar},{ag},{ab},0.5);
                border-radius:4px;display:flex;gap:0.65rem;align-items:flex-start;">
      <span style="font-size:0.95rem;line-height:1.5;opacity:0.8;">{icon}</span>
      <div>
        <span style="font-family:Syne,sans-serif;font-size:0.75rem;font-weight:700;
                     color:{BASE['white']};">{title} </span>
        <span style="font-family:Syne,sans-serif;font-size:0.73rem;
                     color:{BASE['mid']};line-height:1.6;">{body}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def ui_campaign_selector(T, tab_key):
    """Selector row — returns selected campaign key."""
    ar, ag, ab = hex_rgb(T["accent"])

    st.markdown(f"""
    <div style="padding:0 2.5rem;margin-top:1.8rem;margin-bottom:0;">
      <div style="background:{BASE['surface']};border:1px solid rgba(255,255,255,0.06);
                  border-radius:8px;padding:1rem 1.3rem;">
    """, unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        selected = st.selectbox(
            "Automação",
            list(CAMPANHAS.keys()),
            index=0,
            key=f"camp_{tab_key}",
            label_visibility="collapsed",
        )
    with col_info:
        info = CAMPANHAS[selected]
        st.markdown(f"""
        <div style="padding:0.4rem 0;display:flex;align-items:center;gap:0.5rem;">
          <span style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;
                       color:rgba({ar},{ag},{ab},0.5);letter-spacing:1px;">{info['emoji']}</span>
          <span style="font-family:'Syne',sans-serif;font-size:0.76rem;
                       color:{BASE['mid']};line-height:1.5;">{info['desc']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    return selected


def ui_coming_soon(title, subtitle, T, tab_key):
    ar, ag, ab = hex_rgb(T["accent"])
    if ui_topbar(title, subtitle, T, tab_key):
        pass
    st.markdown(f"""
    <div style="padding:6rem 2.5rem;display:flex;flex-direction:column;
                align-items:center;justify-content:center;gap:1.2rem;text-align:center;">
      <div style="width:52px;height:52px;border-radius:50%;
                  border:1px solid {T['border_hi']};
                  background:rgba({ar},{ag},{ab},0.06);
                  display:flex;align-items:center;justify-content:center;">
        <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="6" fill="rgba({ar},{ag},{ab},0.35)"/>
          <path d="M7 23V11l9 8 9-8v12" stroke="{T['accent_lt']}" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
      </div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                  letter-spacing:2px;color:{BASE['text']};text-transform:uppercase;">
        Em breve
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:0.78rem;
                  color:{BASE['mid']};max-width:300px;line-height:1.9;">
        Conecte a planilha ManyChat do ecossistema
        <span style="color:{T['accent_lt']};font-weight:600;">{title}</span>
        para ativar esta aba.
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;
                  letter-spacing:2.5px;text-transform:uppercase;
                  color:rgba({ar},{ag},{ab},0.6);
                  border:1px solid rgba({ar},{ag},{ab},0.22);
                  border-radius:3px;padding:0.4rem 1rem;">
        aguardando conexão manychat
      </div>
    </div>
    """, unsafe_allow_html=True)


def ui_footer(total, title, T):
    ar, ag, ab = hex_rgb(T["accent"])
    st.markdown(f"""
    <div style="padding:1.4rem 2.5rem 2.2rem;margin-top:2.4rem;
                border-top:1px solid rgba(255,255,255,0.04);
                display:flex;justify-content:space-between;align-items:center;gap:1rem;">
      <div style="display:flex;align-items:center;gap:0.6rem;">
        <svg width="14" height="14" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="5" fill="rgba({ar},{ag},{ab},0.3)"/>
          <path d="M7 23V11l9 8 9-8v12" stroke="{T['accent_lt']}" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;
                     letter-spacing:2px;color:{BASE['muted']};text-transform:uppercase;">
          We Love · ManyChat Analytics
        </span>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;
                   letter-spacing:1.5px;color:{BASE['muted']};text-transform:uppercase;
                   opacity:0.75;">
        {total:,} contatos · {title}
      </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  VIEWS
# ─────────────────────────────────────────────────────────────────────────────

def render_consolidated(df, M, T):
    total = len(df)
    if total == 0:
        st.warning("Planilha vazia — nenhum dado para exibir.")
        return

    specific = {k: v for k, v in CAMPANHAS.items() if v["cols"] is not None}

    # ── KPIs ──────────────────────────────────────────────────────────────────
    ui_section_label("Visão Geral · Todos os Contatos ManyChat", T)

    kpi_items = [{
        "value":    f"{total:,}",
        "label":    "Total na Base",
        "sub":      "todos os contatos",
        "note":     "soma de todas as automações",
        "is_total": True,
    }]
    for key, info in specific.items():
        topo_v = M.get(info["cols"][0], 0)
        sub_v  = M.get(info["kpi_sub_col"], 0)
        kpi_items.append({
            "value": f"{topo_v:,}",
            "label": info["label_resumo"],
            "sub":   f"{info['kpi_sub_label']} {fmt_pct(topo_v, sub_v)}",
            "note":  info["kpi_note"],
        })
    ui_kpi_row(kpi_items, T)

    # ── Funnels ───────────────────────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Funis de Conversão · Por Automação ManyChat", T)
    ui_info_box(
        "⚡", "Leitura dos funis:",
        "Cada bloco é uma etapa da automação ManyChat. O % mostra o alcance relativo ao topo. "
        "Quedas bruscas indicam onde revisar a mensagem ou o gatilho.",
        T,
    )

    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        fcols = st.columns(len(specific), gap="small")
        for col, (key, info) in zip(fcols, specific.items()):
            vals = [M.get(c, 0) for c in info["cols"]]
            with col:
                st.plotly_chart(
                    chart_funnel(info["etapas"], vals, info["label_resumo"].upper(), T),
                    use_container_width=True, config={"displayModeBar": False},
                )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Distribution ──────────────────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Distribuição de Contatos · Por Automação", T)
    ui_info_box(
        "📡", "Volume vs. conversão:",
        "Volume alto não garante resultado — o que importa é quantos chegam ao Wpp ou ao site.",
        T,
    )

    canal_l = [info["label_resumo"] for info in specific.values()]
    canal_v = [M.get(info["cols"][0], 0) for info in specific.values()]

    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        cb, cd = st.columns([3, 2], gap="large")
        with cb:
            st.plotly_chart(chart_bar_h(canal_l, canal_v, T),
                            use_container_width=True, config={"displayModeBar": False})
        with cd:
            st.plotly_chart(chart_donut(canal_l, canal_v, T),
                            use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Conversion ────────────────────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Taxa de Conversão · Todas as Etapas ManyChat", T)
    ui_info_box(
        "🎯", "O que é taxa de conversão:",
        "% de contatos que avançaram de uma etapa para outra dentro da automação ManyChat. "
        "Quanto maior, mais eficaz é o fluxo.",
        T,
    )

    stages, rates = [], []
    for key, info in specific.items():
        topo = M.get(info["cols"][0], 0)
        for col, etapa in zip(info["cols"][1:], info["etapas"][1:]):
            stages.append(f"{info['label_resumo']} → {etapa}")
            rates.append(safe_pct(topo, M.get(col, 0)))

    valid = [(s, r) for s, r in zip(stages, rates) if r > 0]

    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        if valid:
            cc, ci = st.columns([3, 2], gap="large")
            with cc:
                st.plotly_chart(
                    chart_conv_bars(stages, rates, T),
                    use_container_width=True, config={"displayModeBar": False},
                )
            with ci:
                st.markdown('<div style="padding-top:0.3rem;">', unsafe_allow_html=True)
                best_s,  best_r  = max(valid, key=lambda x: x[1])
                worst_s, worst_r = min(valid, key=lambda x: x[1])
                total_wpp = sum(
                    M.get(info["kpi_sub_col"], 0)
                    for info in specific.values()
                    if "Wpp" in (info["kpi_sub_label"] or "")
                )
                ui_insight_strip([
                    ("🏆", "Melhor automação",  f"{best_r:.1f}%",  best_s),
                    ("⚠️", "Ponto de atenção",  f"{worst_r:.1f}%", worst_s),
                    ("💬", "Total → Wpp",        f"{total_wpp:,}",  "contatos que chegaram ao WhatsApp"),
                ], T)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para calcular taxas de conversão.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Dados Completos · Todas as Etapas de Automação", T)
    ui_info_box(
        "📋", "Tabela completa:",
        "Número exato de contatos em cada etapa de cada automação ManyChat, com % do total da base.",
        T,
    )
    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        rows = [
            (col, M[col], f"{M[col] / total * 100:.1f}%" if total else "—")
            for col in df.columns
        ]
        st.plotly_chart(
            chart_table(rows, T), use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)


def render_campaign(selected, M, T):
    info   = CAMPANHAS[selected]
    cols_c = info["cols"]
    etapas = info["etapas"]
    values = [M.get(c, 0) for c in cols_c]
    topo   = values[0]

    if topo == 0:
        st.warning(f"Nenhum contato registrado para **{selected}** ainda.")
        return

    ar, ag, ab = hex_rgb(T["accent"])

    # ── KPIs ──────────────────────────────────────────────────────────────────
    ui_section_label(f"Resumo · {selected}", T)
    ui_info_box(
        info["emoji"], f"Automação ManyChat: {selected}",
        info["desc"] + " — selecione 'Todas as Campanhas' para a visão consolidada.",
        T,
    )

    kpi_items = []
    for i, (col, etapa) in enumerate(zip(cols_c, etapas)):
        v   = values[i]
        sub = "entrada da automação" if i == 0 else f"→ {fmt_pct(topo, v)} do topo"
        kpi_items.append({"value": f"{v:,}", "label": etapa, "sub": sub, "note": ""})
    ui_kpi_row(kpi_items, T)

    # ── Funnel + step breakdown ───────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Funil da Automação · Etapa a Etapa", T)

    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        col_f, col_s = st.columns([2, 1], gap="large")

        with col_f:
            st.plotly_chart(
                chart_funnel(etapas, values, selected.upper(), T),
                use_container_width=True, config={"displayModeBar": False},
            )

        with col_s:
            st.markdown(f"""
            <div style="padding-top:0.4rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.48rem;
                          font-weight:500;letter-spacing:3px;text-transform:uppercase;
                          color:{T['accent_lt']};margin-bottom:1rem;">
                Progressão por etapa
              </div>
            """, unsafe_allow_html=True)

            for i, (etapa, v) in enumerate(zip(etapas, values)):
                pct_top  = safe_pct(topo, v)
                bar_w    = max(3, int(pct_top))
                drop_html = ""
                if i > 0:
                    drop     = values[i-1] - v
                    drop_pct = safe_pct(values[i-1], drop)
                    drop_html = (
                        f'<span style="color:#E05050;opacity:0.9;font-size:0.58rem;"> '
                        f'▼ {drop:,} ({drop_pct:.0f}%)</span>'
                    )
                st.markdown(f"""
                <div style="margin-bottom:0.9rem;">
                  <div style="display:flex;justify-content:space-between;
                              align-items:baseline;margin-bottom:0.22rem;">
                    <span style="font-family:'Syne',sans-serif;font-size:0.73rem;
                                 color:{BASE['text']};font-weight:600;">{etapa}</span>
                    <span style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;
                                 color:{BASE['white']};letter-spacing:0.5px;">{v:,}</span>
                  </div>
                  <div style="height:3px;background:{BASE['surface3']};
                              border-radius:2px;overflow:hidden;">
                    <div style="height:100%;width:{bar_w}%;
                                background:rgba({ar},{ag},{ab},0.65);
                                border-radius:2px;"></div>
                  </div>
                  <div style="font-family:'JetBrains Mono',monospace;
                              font-size:0.55rem;color:{BASE['mid']};margin-top:0.12rem;">
                    {pct_top:.1f}% do topo{drop_html}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Conversion bars ───────────────────────────────────────────────────────
    if len(values) > 1:
        ui_thin_divider(T)
        ui_section_label("Taxa de Conversão · Topo → Cada Etapa", T)
        labels_r = [f"{etapas[0]} → {e}" for e in etapas[1:]]
        rates_r  = [safe_pct(topo, v) for v in values[1:]]
        with st.container():
            st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
            st.plotly_chart(
                chart_conv_bars(labels_r, rates_r, T),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    ui_thin_divider(T)
    ui_section_label("Dados Detalhados · Esta Automação ManyChat", T)
    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        rows = [(e, v, f"{safe_pct(topo, v):.1f}%") for e, v in zip(etapas, values)]
        st.plotly_chart(
            chart_table(rows, T), use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ECOSYSTEM TAB  —  reusable for any country / ecosystem
# ─────────────────────────────────────────────────────────────────────────────
def render_ecosystem_tab(sheet_url, title, subtitle, T, tab_key):
    if ui_topbar(title, subtitle, T, tab_key):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("Sincronizando dados ManyChat..."):
        try:
            df = load_data()
        except Exception as e:
            st.error(
                f"Não foi possível carregar o Google Sheets. "
                f"Verifique se a planilha está pública.\n\nDetalhe: {e}"
            )
            return

    missing = validate_columns(df)
    if missing:
        st.error(
            "⚠️ Colunas não encontradas na planilha — verifique nomes (espaços, maiúsculas, acentos):\n\n"
            + "\n".join(f"• `{c}`" for c in missing)
        )
        return

    if len(df) == 0:
        st.warning("Planilha carregada mas vazia.")
        return

    M        = build_metrics(df)
    selected = ui_campaign_selector(T, tab_key)

    if CAMPANHAS[selected]["cols"] is None:
        render_consolidated(df, M, T)
    else:
        render_campaign(selected, M, T)

    ui_footer(len(df), title, T)


# ─────────────────────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["LAISE MESQUITA", "WE LOVE CHILE", "WE LOVE PERU"])

with tab1:
    render_ecosystem_tab(
        sheet_url=SHEET_URL,
        title="Laise Mesquita",
        subtitle="We Love · Central de Performance",
        T=THEMES["rose"],
        tab_key="laise",
    )

with tab2:
    ui_coming_soon("We Love Chile", "We Love · Central de Performance", THEMES["red"], "chile")

with tab3:
    ui_coming_soon("We Love Peru", "We Love · Central de Performance", THEMES["green"], "peru")