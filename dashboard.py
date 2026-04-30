import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from functools import lru_cache

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zafra Marketing — ManyChat Analytics",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS  —  Zafra IDV
# ─────────────────────────────────────────────────────────────────────────────
BASE = {
    "bg":        "#F2EDE4",   # papel creme
    "surface":   "#EAE4D9",   # creme escuro
    "surface2":  "#E0D9CC",   # creme mais escuro
    "surface3":  "#D5CCBB",   # bege
    "text":      "#1A1208",   # quase preto
    "muted":     "#7A6E5F",   # marrom médio
    "mid":       "#4A3F30",   # marrom escuro
    "white":     "#FAF7F2",   # off-white
}

THEMES = {
    "rose": {
        "accent":     "#E8600A",
        "accent_lt":  "#FF7A20",
        "accent_dim": "rgba(232,96,10,0.08)",
        "border":     "rgba(232,96,10,0.20)",
        "border_hi":  "rgba(232,96,10,0.50)",
        "accent2":    "#C4175C",
    },
    "red": {
        "accent":     "#C4175C",
        "accent_lt":  "#E02070",
        "accent_dim": "rgba(196,23,92,0.08)",
        "border":     "rgba(196,23,92,0.20)",
        "border_hi":  "rgba(196,23,92,0.50)",
        "accent2":    "#E8600A",
    },
    "green": {
        "accent":     "#2B7A3D",
        "accent_lt":  "#38A052",
        "accent_dim": "rgba(43,122,61,0.08)",
        "border":     "rgba(43,122,61,0.20)",
        "border_hi":  "rgba(43,122,61,0.50)",
        "accent2":    "#E8600A",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  CAMPAIGN DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
CAMPANHAS = {
    "Todas as Campanhas": {
        "emoji": "◈", "desc": "Visão consolidada de todas as automações ManyChat ativas.",
        "cols": None, "etapas": None, "label_resumo": None,
        "kpi_sub_col": None, "kpi_sub_label": None, "kpi_note": None,
    },
    "Acesso Comercial": {
        "emoji": "◆", "desc": "Automação de entrada pelo fluxo comercial direto.",
        "cols": ["Comercial (Iniciou)", "Comercial (clicou em quero saber mais)", "Comercial (Clicou Wpp)"],
        "etapas": ["Iniciou", "Quero Saber Mais", "Clicou no Wpp"],
        "label_resumo": "Acesso Comercial",
        "kpi_sub_col": "Comercial (Clicou Wpp)", "kpi_sub_label": "→ Wpp", "kpi_note": "Fluxo comercial direto",
    },
    "Campanha Comunidade": {
        "emoji": "◈", "desc": "Automação de leads da campanha da comunidade.",
        "cols": ["Campanha Comunidade (Iniciou)", "Campanha Comunidade (clicou em quero saber mais)", "Campanha Comunidade (Clicou Wpp)"],
        "etapas": ["Iniciou", "Quero Saber Mais", "Clicou no Wpp"],
        "label_resumo": "Comunidade",
        "kpi_sub_col": "Campanha Comunidade (Clicou Wpp)", "kpi_sub_label": "→ Wpp", "kpi_note": "Campanha da comunidade",
    },
    "We Love Rental – Comunidade": {
        "emoji": "◇", "desc": "Automação do fluxo de aluguel da comunidade We Love.",
        "cols": ["We Love Rental - Comunidade (Iniciou)", "We Love Rental - Comunidade (Acessou site)"],
        "etapas": ["Iniciou", "Acessou o Site"],
        "label_resumo": "WL Rental",
        "kpi_sub_col": "We Love Rental - Comunidade (Acessou site)", "kpi_sub_label": "→ Site", "kpi_note": "Fluxo de aluguel",
    },
    "Caderno Secreto": {
        "emoji": "▣", "desc": "Automação de leads captados pelo Caderno Secreto.",
        "cols": ["Caderno Secreto (Iniciou)", "Caderno Secreto (clicou em saber mais)", "Caderno Secreto (Mandou wpp)", "Caderno Secreto (Acessou)", "Caderno Secreto (Clicou Wpp)"],
        "etapas": ["Iniciou", "Saber Mais", "Mandou Wpp", "Acessou", "Clicou Wpp"],
        "label_resumo": "Caderno Secreto",
        "kpi_sub_col": "Caderno Secreto (Clicou Wpp)", "kpi_sub_label": "→ Wpp", "kpi_note": "Caderno Secreto",
    },
}

ALL_REQUIRED_COLS = [col for info in CAMPANHAS.values() if info["cols"] is not None for col in info["cols"]]

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  Zafra Editorial Magazine
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&family=DM+Mono:wght@300;400;500&display=swap');

:root {{
  --bg:       {BASE['bg']};
  --surface:  {BASE['surface']};
  --surface2: {BASE['surface2']};
  --surface3: {BASE['surface3']};
  --text:     {BASE['text']};
  --muted:    {BASE['muted']};
  --mid:      {BASE['mid']};
  --white:    {BASE['white']};
  --orange:   #E8600A;
  --magenta:  #C4175C;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"] {{
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}}

[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.055'/%3E%3C/svg%3E");
    background-size: 200px;
    opacity: 0.8;
    mix-blend-mode: multiply;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}

[data-testid="block-container"] {{ padding: 0 !important; max-width: 100% !important; }}

[data-testid="stTabs"] > div:first-child {{
    background: var(--bg) !important;
    border-bottom: 2px solid var(--text) !important;
    padding: 0 2.5rem !important;
    gap: 0 !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 500 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 1rem 1.4rem !important;
    margin-bottom: -2px !important;
    transition: color .2s, border-color .2s !important;
}}
button[data-baseweb="tab"]:hover {{ color: var(--text) !important; }}
button[aria-selected="true"][data-baseweb="tab"] {{
    color: var(--orange) !important;
    border-bottom: 2px solid var(--orange) !important;
    background: transparent !important;
}}
[data-testid="stTabsContent"] {{ padding: 0 !important; background: transparent !important; }}

.stButton > button {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.58rem !important;
    font-weight: 500 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text) !important;
    background: transparent !important;
    border: 1.5px solid var(--text) !important;
    border-radius: 2px !important;
    padding: 0.4rem 1rem !important;
    transition: all .2s !important;
}}
.stButton > button:hover {{
    color: var(--white) !important;
    background: var(--text) !important;
}}

.js-plotly-plot, .plotly, .stPlotlyChart > div {{ background: transparent !important; }}
[data-testid="column"] > div:first-child {{ padding: 0 !important; }}

[data-testid="stSelectbox"] label {{ display: none !important; }}
[data-testid="stSelectbox"] > div > div {{
    background: var(--white) !important;
    border: 1.5px solid var(--text) !important;
    border-radius: 2px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}}

[data-testid="stSpinner"] > div {{ border-top-color: var(--orange) !important; }}

[data-testid="stAlert"] {{
    background: var(--surface) !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    border-left: 3px solid var(--orange) !important;
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
        font=dict(family="DM Sans", color=BASE["mid"], size=11),
        margin=dict(l=4, r=4, t=20, b=4),
        **kw,
    )

# ─────────────────────────────────────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def chart_funnel(labels, values, title, T):
    n = len(labels)
    ar, ag, ab = hex_rgb(T["accent"])
    alphas = [round(1.0 - i * (0.5 / max(n - 1, 1)), 2) for i in range(n)]
    colors = [f"rgba({ar},{ag},{ab},{a})" for a in alphas]
    height = max(200, min(480, n * 76))
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textposition="inside",
        texttemplate="<b>%{value:,}</b><br><span style='font-size:9px;opacity:.7'>%{percentInitial:.0%}</span>",
        textfont=dict(color=BASE["white"], family="DM Sans", size=11),
        connector=dict(fillcolor=BASE["surface"], line=dict(color=f"rgba({ar},{ag},{ab},0.15)", width=1)),
        marker=dict(color=colors, line=dict(color=f"rgba({ar},{ag},{ab},0.25)", width=1)),
    ))
    fig.update_layout(
        **base_layout(height=height),
        title=dict(text=title, font=dict(family="DM Mono", size=8, color=BASE["muted"]), x=0.5, y=0.99),
    )
    return fig

def chart_bar_h(labels, values, T):
    ar, ag, ab = hex_rgb(T["accent"])
    mx = max(values) if values else 1
    colors = [f"rgba({ar},{ag},{ab},{round(0.3 + 0.7*(v/mx), 2)})" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, cornerradius=2, line=dict(color=BASE["text"], width=0.5)),
        text=[f"<b>{v:,}</b>" for v in values],
        textposition="outside",
        textfont=dict(color=BASE["mid"], family="DM Sans", size=11),
    ))
    fig.update_layout(
        **base_layout(height=max(180, len(labels) * 50)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, mx * 1.3]),
        yaxis=dict(showgrid=False, tickfont=dict(family="DM Sans", size=11, color=BASE["mid"])),
    )
    return fig

def chart_donut(labels, values, T):
    palette = ["#E8600A", "#C4175C", "#4A3F30", "#7A6E5F", "#D5CCBB"]
    n = len(labels)
    colors = palette[:n]
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=colors, line=dict(color=BASE["bg"], width=3)),
        textfont=dict(color=BASE["mid"], family="DM Sans", size=10),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:,} contatos — %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **base_layout(height=240),
        showlegend=True,
        legend=dict(font=dict(family="DM Sans", size=10, color=BASE["mid"]), bgcolor="rgba(0,0,0,0)", x=1.0, y=0.5),
        annotations=[dict(
            text=f"<b>{total:,}</b>", x=0.5, y=0.5, showarrow=False,
            font=dict(color=BASE["text"], family="Playfair Display", size=28),
        )],
    )
    return fig

def chart_conv_bars(stages, rates, T):
    ar, ag, ab = hex_rgb(T["accent"])
    safe = [r if r is not None else 0.0 for r in rates]
    mx = max(safe) if safe else 1
    colors = [
        f"rgba({ar},{ag},{ab},{round(0.25 + 0.75*(r/max(mx,1)), 2)})" if r
        else f"rgba({ar},{ag},{ab},0.12)"
        for r in safe
    ]
    texts = [f"<b>{r:.1f}%</b>" if r else "—" for r in safe]
    fig = go.Figure(go.Bar(
        x=safe, y=stages, orientation="h",
        marker=dict(color=colors, cornerradius=2, line=dict(color=BASE["text"], width=0.5)),
        text=texts, textposition="outside",
        textfont=dict(color=BASE["mid"], family="DM Sans", size=11),
    ))
    fig.update_layout(
        **base_layout(height=max(200, len(stages) * 44)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 125]),
        yaxis=dict(showgrid=False, tickfont=dict(family="DM Sans", size=10.5, color=BASE["mid"])),
    )
    return fig

def chart_table(rows, T):
    ar, ag, ab = hex_rgb(T["accent"])
    row_fill = [BASE["surface"] if i % 2 == 0 else BASE["white"] for i in range(len(rows))]
    fig = go.Figure(go.Table(
        columnwidth=[380, 110, 100],
        header=dict(
            values=["<b>ETAPA / AUTOMAÇÃO MANYCHAT</b>", "<b>CONTATOS</b>", "<b>% TOTAL</b>"],
            fill_color=BASE["text"],
            font=dict(color=BASE["bg"], family="DM Mono", size=9),
            align=["left", "center", "center"],
            height=36,
            line_color=BASE["text"],
        ),
        cells=dict(
            values=[[r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]],
            fill_color=[row_fill],
            font=dict(color=[BASE["text"], BASE["text"], f"rgba({ar},{ag},{ab},0.9)"], family="DM Sans", size=11),
            align=["left", "center", "center"],
            height=32,
            line_color=BASE["surface3"],
        ),
    ))
    fig.update_layout(**base_layout(height=len(rows) * 32 + 50))
    return fig

# ─────────────────────────────────────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def ui_topbar(title, subtitle, T, tab_key):
    ar, ag, ab = hex_rgb(T["accent"])
    clicked = False
    col_main, col_btn = st.columns([10, 1])

    with col_main:
        st.markdown(f"""
        <div style="padding: 2.8rem 2.5rem 0; position:relative; overflow:hidden;">
          <div style="position:absolute;top:-1.5rem;right:2rem;
                      font-family:'Playfair Display',serif;
                      font-size:14rem;font-weight:900;font-style:italic;
                      color:rgba({ar},{ag},{ab},0.06);
                      line-height:1;pointer-events:none;user-select:none;letter-spacing:-5px;">
            DATA
          </div>

          <!-- Zafra wordmark -->
          <div style="display:inline-flex;align-items:center;gap:0.6rem;margin-bottom:1.4rem;">
            <div style="width:32px;height:32px;background:{BASE['text']};
                        display:flex;align-items:center;justify-content:center;
                        border-radius:2px;margin-right:8px;">
              <span style="font-family:'Playfair Display',serif;font-size:1.1rem;
                           font-weight:900;color:{BASE['bg']};line-height:1;">Z</span>
            </div>
            <span style="font-family:'Playfair Display',serif;font-size:1.3rem;
                         font-weight:900;color:{BASE['text']};letter-spacing:-0.5px;">zafra</span>
            <div style="width:1px;height:18px;background:rgba(0,0,0,0.2);"></div>
            <span style="font-family:'DM Mono',monospace;font-size:0.52rem;font-weight:500;
                         letter-spacing:3px;text-transform:uppercase;color:{BASE['muted']};">
              Marketing · Analytics
            </span>
            <div style="background:rgba({ar},{ag},{ab},1);border-radius:2px;
                        padding:0.22rem 0.65rem;margin-left:0.3rem;">
              <span style="font-family:'DM Mono',monospace;font-size:0.5rem;
                           font-weight:500;letter-spacing:2.5px;text-transform:uppercase;
                           color:{BASE['white']};">ManyChat</span>
            </div>
          </div>

          <br/>
          <div style="display:flex;align-items:flex-end;gap:1rem;flex-wrap:wrap;margin-top:0.6rem;">
            <h1 style="font-family:'Playfair Display',serif;
                       font-size:clamp(2.6rem,5vw,4.8rem);
                       font-weight:900;font-style:italic;
                       color:{BASE['text']};line-height:0.9;letter-spacing:-1px;">
              {title}
            </h1>
            <span style="font-family:'DM Sans',sans-serif;font-size:0.78rem;
                         color:{BASE['muted']};font-weight:400;
                         margin-bottom:0.5rem;font-style:italic;">
              {subtitle}
            </span>
          </div>

          <div style="margin-top:1.6rem;display:flex;align-items:center;gap:0.8rem;">
            <div style="height:4px;width:3rem;background:{T['accent']};border-radius:1px;"></div>
            <div style="height:1px;flex:1;background:rgba(0,0,0,0.12);"></div>
            <div style="height:4px;width:1rem;background:{T.get('accent2','#C4175C')};border-radius:1px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown('<div style="padding-top:3.4rem;padding-right:1rem;">', unsafe_allow_html=True)
        if st.button("↺ sync", key=f"sync_{tab_key}"):
            clicked = True
        st.markdown(
            f'<div style="font-family:DM Mono,monospace;font-size:0.45rem;'
            f'color:{BASE["muted"]};text-align:right;margin-top:0.3rem;letter-spacing:1px;'
            f'text-transform:uppercase;">auto 5m</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    return clicked


def ui_section_label(text, T, margin_top="2.4rem"):
    st.markdown(f"""
    <div style="padding: 0 2.5rem; margin-top:{margin_top}; margin-bottom:0.7rem;
                display:flex; align-items:center; gap:0.7rem;">
      <div style="width:8px;height:8px;background:{T['accent']};
                  transform:rotate(45deg);flex-shrink:0;"></div>
      <span style="font-family:'DM Mono',monospace;font-size:0.52rem;font-weight:500;
                   letter-spacing:3px;text-transform:uppercase;color:{BASE['mid']};">{text}</span>
      <div style="flex:1;height:1px;background:rgba(0,0,0,0.1);"></div>
    </div>
    """, unsafe_allow_html=True)


def ui_thin_divider(T):
    st.markdown(
        '<div style="height:1px;margin:0.6rem 2.5rem 0;background:rgba(0,0,0,0.08);"></div>',
        unsafe_allow_html=True,
    )


def ui_kpi_row(items, T):
    ar, ag, ab = hex_rgb(T["accent"])
    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        cols = st.columns(len(items))
        for col, item in zip(cols, items):
            is_total   = item.get("is_total", False)
            bg_color   = BASE["text"] if is_total else BASE["white"]
            val_color  = BASE["bg"] if is_total else BASE["text"]
            lbl_color  = "rgba(242,237,228,0.65)" if is_total else BASE["muted"]
            sub_color  = T["accent_lt"] if is_total else T["accent"]
            border_css = "" if is_total else f"border: 1.5px solid {BASE['surface3']};"
            ghost      = item["value"].replace(",", "").replace("%", "")

            sub_h = (
                f'<div style="font-family:DM Sans,sans-serif;font-size:0.72rem;font-weight:700;'
                f'color:{sub_color};margin-top:0.4rem;">{item["sub"]}</div>'
            ) if item.get("sub") else ""
            note_h = (
                f'<div style="font-family:DM Mono,monospace;font-size:0.52rem;'
                f'color:{lbl_color};margin-top:0.3rem;font-style:italic;">{item["note"]}</div>'
            ) if item.get("note") else ""

            col.markdown(f"""
            <div style="background:{bg_color};{border_css}border-radius:4px;
                        padding:1.4rem 1.5rem 1.3rem;position:relative;
                        overflow:hidden;min-height:138px;">
              <div style="position:absolute;bottom:-18px;right:-4px;
                          font-family:'Playfair Display',serif;font-size:5rem;
                          font-weight:900;line-height:1;
                          color:rgba(0,0,0,0.04);pointer-events:none;user-select:none;">
                {ghost}
              </div>
              <div style="position:absolute;top:1rem;right:1.1rem;
                          width:8px;height:8px;
                          border:1.5px solid rgba({'242,237,228' if is_total else '26,18,8'},0.2);
                          transform:rotate(45deg);"></div>
              <div style="font-family:'Playfair Display',serif;font-size:3rem;
                          font-weight:900;font-style:italic;color:{val_color};
                          line-height:1;letter-spacing:-1px;">
                {item['value']}
              </div>
              <div style="font-family:'DM Mono',monospace;font-size:0.58rem;font-weight:500;
                          letter-spacing:2.5px;text-transform:uppercase;
                          color:{lbl_color};margin-top:0.5rem;">
                {item['label']}
              </div>
              {sub_h}{note_h}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def ui_insight_strip(cards, T):
    cols = st.columns(len(cards))
    for col, (icon, tag, value, sub) in zip(cols, cards):
        sub_h = (
            f'<div style="font-size:0.65rem;color:{BASE["muted"]};margin-top:0.2rem;'
            f'font-family:DM Sans,sans-serif;line-height:1.5;font-style:italic;">{sub}</div>'
        ) if sub else ""
        col.markdown(f"""
        <div style="background:{BASE['white']};border:1.5px solid {BASE['surface3']};
                    border-radius:4px;padding:0.9rem 1rem;
                    display:flex;gap:0.65rem;align-items:flex-start;">
          <span style="font-size:1rem;margin-top:0.05rem;flex-shrink:0;">{icon}</span>
          <div>
            <div style="font-family:DM Mono,monospace;font-size:0.47rem;font-weight:500;
                        letter-spacing:2.5px;text-transform:uppercase;
                        color:{T['accent']};margin-bottom:0.2rem;">{tag}</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.6rem;
                        font-style:italic;color:{BASE['text']};line-height:1.1;">{value}</div>
            {sub_h}
          </div>
        </div>
        """, unsafe_allow_html=True)


def ui_info_box(icon, title, body, T):
    st.markdown(f"""
    <div style="margin:0 2.5rem 1rem;padding:0.85rem 1.1rem;
                background:{BASE['white']};border:1px solid rgba(0,0,0,0.1);
                border-left:3px solid {T['accent']};border-radius:2px;
                display:flex;gap:0.65rem;align-items:flex-start;">
      <span style="font-size:0.95rem;line-height:1.5;">{icon}</span>
      <div>
        <span style="font-family:DM Sans,sans-serif;font-size:0.78rem;font-weight:700;
                     color:{BASE['text']};">{title} </span>
        <span style="font-family:DM Sans,sans-serif;font-size:0.75rem;
                     color:{BASE['muted']};line-height:1.7;font-style:italic;">{body}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def ui_campaign_selector(T, tab_key):
    ar, ag, ab = hex_rgb(T["accent"])
    st.markdown(f"""
    <div style="padding:0 2.5rem;margin-top:1.8rem;margin-bottom:0;">
      <div style="background:{BASE['white']};border:1.5px solid {BASE['surface3']};
                  border-radius:4px;padding:1rem 1.3rem;">
    """, unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        selected = st.selectbox(
            "Automação", list(CAMPANHAS.keys()), index=0,
            key=f"camp_{tab_key}", label_visibility="collapsed",
        )
    with col_info:
        info = CAMPANHAS[selected]
        st.markdown(f"""
        <div style="padding:0.4rem 0;display:flex;align-items:center;gap:0.6rem;">
          <span style="font-family:'Playfair Display',serif;font-size:1.5rem;
                       color:rgba({ar},{ag},{ab},0.5);font-style:italic;">{info['emoji']}</span>
          <span style="font-family:'DM Sans',sans-serif;font-size:0.77rem;
                       color:{BASE['muted']};line-height:1.5;font-style:italic;">{info['desc']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    return selected


def ui_coming_soon(title, subtitle, T, tab_key):
    ar, ag, ab = hex_rgb(T["accent"])
    if ui_topbar(title, subtitle, T, tab_key):
        pass
    st.markdown(f"""
    <div style="padding:5rem 2.5rem;display:flex;flex-direction:column;
                align-items:center;justify-content:center;gap:1.4rem;text-align:center;">
      <div style="width:80px;height:80px;border-radius:50%;
                  border:2px solid {T['accent']};
                  background:rgba({ar},{ag},{ab},0.06);
                  display:flex;align-items:center;justify-content:center;">
        <span style="font-family:'Playfair Display',serif;font-size:2rem;
                     font-weight:900;font-style:italic;color:{T['accent']};">Z</span>
      </div>
      <div style="font-family:'Playfair Display',serif;font-size:3rem;
                  font-weight:900;font-style:italic;color:{BASE['text']};line-height:1;">
        Em breve.
      </div>
      <div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                  color:{BASE['muted']};max-width:320px;line-height:1.9;font-style:italic;">
        Conecte a planilha ManyChat do ecossistema
        <span style="color:{T['accent']};font-weight:700;font-style:normal;">{title}</span>
        para ativar esta aba.
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:0.5rem;
                  letter-spacing:2.5px;text-transform:uppercase;color:{T['accent']};
                  border:1.5px solid {T['accent']};border-radius:2px;padding:0.4rem 1rem;">
        aguardando conexão manychat
      </div>
    </div>
    """, unsafe_allow_html=True)


def ui_footer(total, title, T):
    st.markdown(f"""
    <div style="padding:1.4rem 2.5rem 2.2rem;margin-top:2.4rem;
                border-top:2px solid {BASE['text']};
                display:flex;justify-content:space-between;align-items:center;gap:1rem;">
      <div style="display:flex;align-items:center;gap:0.8rem;">
        <div style="width:24px;height:24px;background:{BASE['text']};
                    display:flex;align-items:center;justify-content:center;border-radius:2px;">
          <span style="font-family:'Playfair Display',serif;font-size:0.85rem;
                       font-weight:900;color:{BASE['bg']};">Z</span>
        </div>
        <span style="font-family:'Playfair Display',serif;font-size:0.9rem;
                     font-weight:700;font-style:italic;color:{BASE['text']};">
          zafra<span style="color:{T['accent']};"> marketing</span>
        </span>
        <span style="font-family:'DM Mono',monospace;font-size:0.5rem;
                     letter-spacing:2px;color:{BASE['muted']};text-transform:uppercase;">
          · Analytics
        </span>
      </div>
      <span style="font-family:'DM Mono',monospace;font-size:0.5rem;
                   letter-spacing:1.5px;color:{BASE['muted']};text-transform:uppercase;">
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

    ui_section_label("Visão Geral · Todos os Contatos ManyChat", T)

    kpi_items = [{
        "value": f"{total:,}", "label": "Total na Base",
        "sub": "todos os contatos", "note": "soma de todas as automações", "is_total": True,
    }]
    for key, info in specific.items():
        topo_v = M.get(info["cols"][0], 0)
        sub_v  = M.get(info["kpi_sub_col"], 0)
        kpi_items.append({
            "value": f"{topo_v:,}", "label": info["label_resumo"],
            "sub": f"{info['kpi_sub_label']} {fmt_pct(topo_v, sub_v)}", "note": info["kpi_note"],
        })
    ui_kpi_row(kpi_items, T)

    ui_thin_divider(T)
    ui_section_label("Funis de Conversão · Por Automação ManyChat", T)
    ui_info_box("⚡", "Leitura dos funis:",
        "Cada bloco é uma etapa da automação ManyChat. O % mostra o alcance relativo ao topo. "
        "Quedas bruscas indicam onde revisar a mensagem ou o gatilho.", T)

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

    ui_thin_divider(T)
    ui_section_label("Distribuição de Contatos · Por Automação", T)
    ui_info_box("📡", "Volume vs. conversão:",
        "Volume alto não garante resultado — o que importa é quantos chegam ao Wpp ou ao site.", T)

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

    ui_thin_divider(T)
    ui_section_label("Taxa de Conversão · Todas as Etapas ManyChat", T)
    ui_info_box("🎯", "O que é taxa de conversão:",
        "% de contatos que avançaram de uma etapa para outra dentro da automação ManyChat. "
        "Quanto maior, mais eficaz é o fluxo.", T)

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
                    ("🏆", "Melhor automação", f"{best_r:.1f}%", best_s),
                    ("⚠️", "Ponto de atenção", f"{worst_r:.1f}%", worst_s),
                    ("💬", "Total → Wpp", f"{total_wpp:,}", "contatos que chegaram ao WhatsApp"),
                ], T)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para calcular taxas de conversão.")
        st.markdown('</div>', unsafe_allow_html=True)

    ui_thin_divider(T)
    ui_section_label("Dados Completos · Todas as Etapas de Automação", T)
    ui_info_box("📋", "Tabela completa:",
        "Número exato de contatos em cada etapa de cada automação ManyChat, com % do total da base.", T)
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

    ui_section_label(f"Resumo · {selected}", T)
    ui_info_box(
        info["emoji"], f"Automação ManyChat: {selected}",
        info["desc"] + " — selecione 'Todas as Campanhas' para a visão consolidada.", T,
    )

    kpi_items = []
    for i, (col, etapa) in enumerate(zip(cols_c, etapas)):
        v   = values[i]
        sub = "entrada da automação" if i == 0 else f"→ {fmt_pct(topo, v)} do topo"
        kpi_items.append({"value": f"{v:,}", "label": etapa, "sub": sub, "note": ""})
    ui_kpi_row(kpi_items, T)

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
              <div style="font-family:'DM Mono',monospace;font-size:0.48rem;
                          font-weight:500;letter-spacing:3px;text-transform:uppercase;
                          color:{T['accent']};margin-bottom:1rem;">
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
                        f'<span style="color:#C4175C;font-size:0.58rem;"> '
                        f'▼ {drop:,} ({drop_pct:.0f}%)</span>'
                    )
                st.markdown(f"""
                <div style="margin-bottom:0.9rem;">
                  <div style="display:flex;justify-content:space-between;
                              align-items:baseline;margin-bottom:0.22rem;">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.73rem;
                                 color:{BASE['text']};font-weight:600;">{etapa}</span>
                    <span style="font-family:'Playfair Display',serif;font-size:1.2rem;
                                 font-style:italic;color:{BASE['text']};font-weight:900;">{v:,}</span>
                  </div>
                  <div style="height:3px;background:{BASE['surface3']};border-radius:1px;overflow:hidden;">
                    <div style="height:100%;width:{bar_w}%;
                                background:rgba({ar},{ag},{ab},0.7);border-radius:1px;"></div>
                  </div>
                  <div style="font-family:'DM Mono',monospace;font-size:0.52rem;
                              color:{BASE['muted']};margin-top:0.12rem;">
                    {pct_top:.1f}% do topo{drop_html}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

    ui_thin_divider(T)
    ui_section_label("Dados Detalhados · Esta Automação ManyChat", T)
    with st.container():
        st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
        rows = [(e, v, f"{safe_pct(topo, v):.1f}%") for e, v in zip(etapas, values)]
        st.plotly_chart(
            chart_table(rows, T), use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)


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
            "Colunas não encontradas na planilha:\n\n"
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
