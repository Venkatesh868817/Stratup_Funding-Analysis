#!/usr/bin/env python
# coding: utf-8

# ============================================================
# UNIFIED STARTUP DASHBOARD
# Integrates:
#   - Executive Dashboard (main controller with global filters)
#   - Startup Performance Dashboard (render_performance)
#   - Advanced Insights Dashboard (render_insights)
# One dataset → One filter system → Multiple dashboards
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, ctx

# ==============================
# LOAD & PREPARE DATA
# ==============================

df = pd.read_excel("Startup_Cleaned_Dataset_.xlsx")

# Standardise column names used by the Executive Dashboard
df = df.rename(columns={
    "Startup_Name":            "Startup",
    "Industry_Vertical_Std":   "Industry",
    "City_Location_Std":       "City",
    "Investment_Type_std":     "Investment_Type",
    "Investors_Name_Std":      "Investor",
    "Amount in USD":           "Amount"
})

df["Year"] = df["Year"].astype(str)

# Clean percentage columns (Dashboard 2 needs these)
for col in ["Profit Margin (%)", "Revenue Growth Rate (%)"]:
    if col in df.columns:
        df[col] = (
            df[col].astype(str).str.replace("%", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ==============================
# COLOUR PALETTE
# ==============================

colors = {
    "background": "#EEF2F7",
    "card_bg":    "white",
    "primary":    "#1F3C88",
    "secondary":  "#2EC4B6",
    "highlight":  "#6C63FF",
    "accent":     "#FF9F1C",
    "text":       "#2B2B2B",
}

# ==============================
# SHARED STYLING HELPERS
# ==============================

CARD_STYLE = {
    "background": "white",
    "borderRadius": "12px",
    "boxShadow": "0 3px 10px rgba(0,0,0,0.08)",
    "padding": "15px",
    "border": "1px solid #E6E6E6",
    "textAlign": "center",
}

PAGE_STYLE = {
    "backgroundColor": colors["background"],
    "padding": "20px",
    "fontFamily": "Segoe UI",
    "maxWidth": "4000px",
    "margin": "auto",
}


def style_chart_executive(fig):
    """Styling used by the Executive Dashboard."""
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI", size=18),
        title={"x": 0.5, "xanchor": "center", "font": {"size": 30}},
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


def style_chart_perf(fig):
    """Styling used by the Performance Dashboard."""
    fig.update_layout(
        plot_bgcolor="#F5F7FB",
        paper_bgcolor="#F5F7FB",
        font=dict(color="#2B2B2B"),
        margin=dict(l=20, r=20, t=50, b=20),
        title_font=dict(size=16),
        title={"x": 0.5, "xanchor": "center"},
    )
    return fig


def style_chart_insights(fig):
    """Styling used by the Advanced Insights Dashboard."""
    fig.update_layout(
        template="plotly_white",
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        title_x=0.5,
    )
    return fig


# ==============================
# DASHBOARD 2 – PERFORMANCE
# render_performance(data) → html.Div
# ==============================

def render_performance(data):
    """
    Renders all Startup Performance charts using the supplied
    filtered DataFrame.  Column names expected:
      Startup, Amount, Monthly Revenue, Annual Burn Rate,
      Customer Acquisition Cost (CAC), Customer Lifetime Value (CLV),
      Active Users, Revenue Growth Rate (%), Profit Margin (%),
      Industry
    """

    perf_card = {
        "background": "white",
        "padding": "15px",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(31,60,136,0.10)",
        "flex": "1",
        "transition": "all 0.3s ease",
    }

    h4_style = {
        "textAlign": "center",
        "width": "100%",
        "display": "block",
        "margin": "0 auto 10px auto",
        "color": "#2EC4B6",
        "fontWeight": "600",
    }

    row_style = {
        "display": "flex",
        "gap": "20px",
        "marginBottom": "20px",
    }

    # ---- fig1: Top 10 Funded Startups ----
    top10 = data.sort_values(by="Amount", ascending=False).head(10)
    fig1 = style_chart_perf(
        px.bar(top10, x="Startup", y="Amount",
               title="Top 10 Funded Startups")
    )

    # ---- fig2: Revenue vs Burn Rate ----
    if "Monthly Revenue" in data.columns and "Annual Burn Rate" in data.columns:
        fig2 = style_chart_perf(
            px.scatter(data, x="Monthly Revenue", y="Annual Burn Rate",
                       title="Revenue vs Burn Rate")
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(title_text="Revenue vs Burn Rate – data unavailable")

    # ---- fig3: CLV vs CAC ----
    cac_col = "Customer Acquisition Cost (CAC)"
    clv_col = "Customer Lifetime Value (CLV)"
    if cac_col in data.columns and clv_col in data.columns:
        fig3 = style_chart_perf(
            px.scatter(data, x=cac_col, y=clv_col,
                       title="CLV vs CAC Analysis")
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(title_text="CLV vs CAC – data unavailable")

    # ---- fig4: Active Users vs Revenue Growth ----
    if "Active Users" in data.columns and "Revenue Growth Rate (%)" in data.columns:
        fig4 = style_chart_perf(
            px.scatter(data, x="Active Users", y="Revenue Growth Rate (%)",
                       title="Active Users vs Revenue Growth")
        )
    else:
        fig4 = go.Figure()
        fig4.update_layout(title_text="Active Users vs Revenue Growth – data unavailable")

    # ---- fig5: Profit Margin by Industry (top 10) ----
    if "Profit Margin (%)" in data.columns and "Industry" in data.columns:
        top_industries = (
            data.groupby("Industry")["Profit Margin (%)"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .index
        )
        df_top = data[data["Industry"].isin(top_industries)]
        fig5 = style_chart_perf(
            px.box(df_top, x="Industry", y="Profit Margin (%)",
                   title="Profit Margin by Industry")
        )
    else:
        fig5 = go.Figure()
        fig5.update_layout(title_text="Profit Margin by Industry – data unavailable")

    return html.Div([

        html.H2("📊 Startup Performance Dashboard",
                style={"textAlign": "center", "marginBottom": "20px",
                       "color": "#1F3C88", "fontWeight": "600"}),

        html.Div([
            html.Div([
                html.H4("📈 Top Funded Startups", style=h4_style),
                dcc.Graph(figure=fig1),
            ], style=perf_card),
            html.Div([
                html.H4("💸 Revenue vs Burn Rate", style=h4_style),
                dcc.Graph(figure=fig2),
            ], style=perf_card),
        ], style=row_style),

        html.Div([
            html.Div([
                html.H4("📊 CLV vs CAC", style=h4_style),
                dcc.Graph(figure=fig3),
            ], style=perf_card),
            html.Div([
                html.H4("🚀 Users vs Growth", style=h4_style),
                dcc.Graph(figure=fig4),
            ], style=perf_card),
        ], style=row_style),

        html.Div([
            html.Div([
                html.H4("🏭 Profit Margin by Industry", style=h4_style),
                dcc.Graph(figure=fig5),
            ], style={**perf_card, "flex": "100%"}),
        ], style=row_style),

    ], style={"backgroundColor": "#F5F7FB", "padding": "20px",
              "borderRadius": "12px"})


# ==============================
# DASHBOARD 3 – ADVANCED INSIGHTS
# render_insights(data) → html.Div
# ==============================

def render_insights(data):
    """
    Renders all Advanced Insights charts using the supplied
    filtered DataFrame.  Column names expected:
      Revenue Growth Rate (%), Profit Margin (%),
      Amount, Investment_Type, Investor
    """

    # ---- fig1: Growth vs Profitability ----
    if "Revenue Growth Rate (%)" in data.columns and "Profit Margin (%)" in data.columns:
        fig1 = px.scatter(
            data,
            x="Revenue Growth Rate (%)",
            y="Profit Margin (%)",
            color="Profit Margin (%)",
            title="Growth vs Profitability",
            color_continuous_scale=[colors["secondary"], colors["highlight"]],
        )
        fig1.add_vline(x=0, line_dash="dash")
        fig1.add_hline(y=0, line_dash="dash")
    else:
        fig1 = go.Figure()
        fig1.update_layout(title_text="Growth vs Profitability – data unavailable")

    # ---- fig2: Funding Outliers ----
    fig2 = px.box(
        data,
        y="Amount",
        title="Funding Outliers",
        color_discrete_sequence=[colors["accent"]],
    )

    # ---- fig3: Funding by Stage (Top 10) ----
    stage_df = (
        data.groupby("Investment_Type")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig3 = px.bar(
        stage_df,
        y="Investment_Type",
        x="Amount",
        orientation="h",
        title="Funding by Stage (Top 10)",
        color_discrete_sequence=["#1F3C88"],
    )

    # ---- fig4: Top Investors ----
    top_investors = (
        data.groupby("Investor")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig4 = px.bar(
        top_investors,
        y="Investor",
        x="Amount",
        orientation="h",
        title="Top Investors by Funding",
        color_discrete_sequence=[colors["highlight"]],
    )

    for fig in [fig1, fig2, fig3, fig4]:
        style_chart_insights(fig)

    return html.Div(
        style={
            "backgroundColor": colors["background"],
            "height": "100%",
            "padding": "10px",
            "fontFamily": "Segoe UI",
            "color": colors["text"],
        },
        children=[
            html.H3(
                "Advanced Insights Dashboard",
                style={"textAlign": "center", "color": colors["primary"],
                       "marginBottom": "10px"},
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gridTemplateRows": "auto auto",
                    "gap": "10px",
                },
                children=[
                    dcc.Graph(figure=fig1, config={"displayModeBar": False}),
                    dcc.Graph(figure=fig2, config={"displayModeBar": False}),
                    dcc.Graph(figure=fig3, config={"displayModeBar": False}),
                    dcc.Graph(figure=fig4, config={"displayModeBar": False}),
                ],
            ),
        ],
    )


# ==============================
# DASH APP INIT
# ==============================

app = Dash(__name__)

# ==============================
# DROPDOWN + HOVER CSS (unchanged from Executive Dashboard)
# ==============================

app.index_string = """
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>Unified Startup Funding Dashboard</title>
{%favicon%}
{%css%}

<style>

/* Dropdown Size */
.Select-control { height:80px !important; min-height:80px !important; }
.Select-placeholder { line-height:80px !important; }
.Select-input { height:80px !important; }
.Select-value { line-height:80px !important; }

/* KPI Hover */
.card-hover { transition:all 0.3s ease; }
.card-hover:hover { transform:translateY(-6px); box-shadow:0 12px 25px rgba(0,0,0,0.18) !important; }

/* Chart Hover */
.chart-card { transition:all 0.3s ease; }
.chart-card:hover { transform:translateY(-5px); box-shadow:0 10px 20px rgba(0,0,0,0.15) !important; }

/* Button Hover */
button:hover { transform:scale(1.02); transition:0.25s; }

/* Tab styling */
.tab-nav { display:flex; gap:8px; margin-bottom:20px; }

</style>
</head>

<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
"""

# ==============================
# LAYOUT
# ==============================

app.layout = html.Div(style=PAGE_STYLE, children=[

    # ── Header ──────────────────────────────────────────────
    html.H1(
        "🏢 Unified Startup Funding Dashboard",
        style={
            "textAlign": "center",
            "color": "white",
            "fontSize": "40px",
            "fontWeight": "700",
            "padding": "20px",
            "marginBottom": "25px",
            "borderRadius": "10px",
            "background": "linear-gradient(90deg,#1F3C88,#6C63FF)",
        },
    ),

    # ── Sidebar + Main content ───────────────────────────────
    html.Div([

        # ── SIDEBAR (filters – unchanged) ────────────────────
        html.Div([

            html.H3("Filters", style={"color": "#1F3C88", "marginBottom": "25px",
                                       "fontSize": "26px", "fontWeight": "800"}),

            html.Div([
                html.Label("📅 Year", style={"fontSize": "25px", "fontWeight": "600",
                                              "marginBottom": "6px"}),
                dcc.Dropdown(
                    id="year",
                    options=[{"label": i, "value": i} for i in sorted(df["Year"].unique())],
                    multi=True,
                    style={"fontSize": "22px"},
                ),
            ], style={"marginBottom": "30px"}),

            html.Div([
                html.Label("🏭 Industry", style={"fontSize": "25px", "fontWeight": "600",
                                                   "marginBottom": "6px"}),
                dcc.Dropdown(
                    id="industry",
                    options=[{"label": i, "value": i}
                             for i in sorted(df["Industry"].dropna().unique())],
                    multi=True,
                    style={"fontSize": "22px"},
                ),
            ], style={"marginBottom": "30px"}),

            html.Div([
                html.Label("📍 City", style={"fontSize": "25px", "fontWeight": "600",
                                              "marginBottom": "6px"}),
                dcc.Dropdown(
                    id="city",
                    options=[{"label": i, "value": i}
                             for i in sorted(df["City"].dropna().unique())],
                    multi=True,
                    style={"fontSize": "22px"},
                ),
            ], style={"marginBottom": "30px"}),

            html.Div([
                html.Label("💰 Investment Type", style={"fontSize": "25px", "fontWeight": "600",
                                                          "marginBottom": "6px"}),
                dcc.Dropdown(
                    id="investment",
                    options=[{"label": i, "value": i}
                             for i in sorted(df["Investment_Type"].dropna().unique())],
                    multi=True,
                    style={"fontSize": "22px"},
                ),
            ], style={"marginBottom": "30px"}),

            html.Button(
                "Reset Filters",
                id="reset-btn",
                n_clicks=0,
                style={
                    "background": "#FF9F1C",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                    "cursor": "pointer",
                    "width": "100%",
                    "fontSize": "28px",
                    "fontWeight": "650",
                    "height": "100px",
                    "boxShadow": "0 4px 10px rgba(0,0,0,0.15)",
                    "marginBottom": "20px",
                },
            ),

            # ── Dashboard selector ───────────────────────────
            html.Hr(style={"borderColor": "#E6E6E6", "marginBottom": "16px"}),
            html.H4("View", style={"color": "#1F3C88", "fontSize": "22px",
                                    "fontWeight": "700", "marginBottom": "12px"}),
            dcc.RadioItems(
                id="dashboard-selector",
                options=[
                    {"label": " 📊 Executive",    "value": "executive"},
                    {"label": " 🚀 Performance",  "value": "performance"},
                    {"label": " 🔍 Insights",     "value": "insights"},
                ],
                value="executive",
                labelStyle={"display": "block", "fontSize": "20px",
                            "marginBottom": "10px", "cursor": "pointer"},
                inputStyle={"marginRight": "8px"},
            ),

        ], style={
            "width": "18%",
            "background": "white",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.08)",
            "display": "flex",
            "flexDirection": "column",
            "minHeight": "100%",
        }),

        # ── MAIN PANEL ────────────────────────────────────────
        html.Div(
            id="main-panel",
            style={"width": "80%", "marginLeft": "20px"},
        ),

    ], style={"display": "flex"}),
])


# ==============================
# UNIFIED CALLBACK
# One filter system → all dashboards
# ==============================

@app.callback(
    # main panel content
    Output("main-panel", "children"),

    # sync filter values on reset
    Output("year",       "value"),
    Output("industry",   "value"),
    Output("city",       "value"),
    Output("investment", "value"),

    Input("year",                "value"),
    Input("industry",            "value"),
    Input("city",                "value"),
    Input("investment",          "value"),
    Input("reset-btn",           "n_clicks"),
    Input("dashboard-selector",  "value"),
)
def update_all(year, industry, city, investment, reset, active_dashboard):

    # ── Reset filters ──────────────────────────────────────
    if ctx.triggered_id == "reset-btn":
        year = industry = city = investment = None

    # ── Apply global filters once ──────────────────────────
    data = df.copy()
    if year:
        data = data[data["Year"].isin(year)]
    if industry:
        data = data[data["Industry"].isin(industry)]
    if city:
        data = data[data["City"].isin(city)]
    if investment:
        data = data[data["Investment_Type"].isin(investment)]

    # ── Route to correct dashboard ─────────────────────────
    if active_dashboard == "performance":
        panel = render_performance(data)
        return panel, year, industry, city, investment

    if active_dashboard == "insights":
        panel = render_insights(data)
        return panel, year, industry, city, investment

    # ── Default: Executive Dashboard ──────────────────────
    total     = data["Amount"].sum()
    startups  = data["Startup"].nunique()
    avg       = data["Amount"].mean()
    investors = data["Investor"].nunique()

    kpis = [
        html.Div([
            html.P("💰 Total Funding",   style={"fontSize": "30px", "fontWeight": "600"}),
            html.H3(f"${total:,.0f}",   style={"fontSize": "36px", "color": "#1F3C88"}),
        ], style={**CARD_STYLE, "borderLeft": "6px solid #1F3C88"}, className="card-hover"),

        html.Div([
            html.P("🏢 Startups",        style={"fontSize": "30px", "fontWeight": "600"}),
            html.H3(startups,            style={"fontSize": "36px", "color": "#2EC4B6"}),
        ], style={**CARD_STYLE, "borderLeft": "6px solid #2EC4B6"}, className="card-hover"),

        html.Div([
            html.P("📈 Avg Funding",     style={"fontSize": "30px", "fontWeight": "600"}),
            html.H3(f"${avg:,.0f}",     style={"fontSize": "36px", "color": "#FF9F1C"}),
        ], style={**CARD_STYLE, "borderLeft": "6px solid #FF9F1C"}, className="card-hover"),

        html.Div([
            html.P("🤝 Investors",       style={"fontSize": "30px", "fontWeight": "600"}),
            html.H3(investors,           style={"fontSize": "36px", "color": "#6C63FF"}),
        ], style={**CARD_STYLE, "borderLeft": "6px solid #6C63FF"}, className="card-hover"),
    ]

    # Trend chart
    trend = data.groupby("Year")["Amount"].sum().reset_index()
    fig1  = style_chart_executive(
        px.line(trend, x="Year", y="Amount", markers=True,
                title="📈 Funding Trend Over Time",
                color_discrete_sequence=["#1F3C88"])
    )
    fig1.update_traces(
        hovertemplate="<b>%{x}</b><br>Funding: %{y:$,.0f}<extra></extra>",
        line=dict(width=5), marker=dict(size=10),
    )

    # Industry bar
    industry_chart = (
        data.groupby("Industry")["Amount"].sum().nlargest(10).reset_index()
    )
    max_ind = industry_chart["Amount"].max()
    industry_chart["color"] = industry_chart["Amount"].apply(
        lambda x: "#FF9F1C" if x == max_ind else "#6C63FF"
    )
    fig2 = style_chart_executive(
        px.bar(industry_chart, x="Amount", y="Industry", orientation="h",
               title="🏭 Top Industries by Funding",
               color="color", color_discrete_map="identity")
    )
    fig2.update_traces(
        hovertemplate="<b>%{y}</b><br>Funding: %{x:$,.0f}<extra></extra>",
        marker_cornerradius=8,
    )
    fig2.update_yaxes(title_standoff=25, ticklabelposition="outside",
                      ticklabelstandoff=12)

    # City bar
    city_chart = (
        data.groupby("City")["Amount"].sum().nlargest(10).reset_index()
    )
    max_city = city_chart["Amount"].max()
    city_chart["color"] = city_chart["Amount"].apply(
        lambda x: "#FF9F1C" if x == max_city else "#2EC4B6"
    )
    fig3 = style_chart_executive(
        px.bar(city_chart, x="City", y="Amount",
               title="📍 Funding by City",
               color="color", color_discrete_map="identity")
    )
    fig3.update_traces(
        hovertemplate="<b>%{x}</b><br>Funding: %{y:$,.0f}<extra></extra>",
        marker_cornerradius=8,
    )

    # Investment type donut
    invest = (
        data.groupby("Investment_Type")["Amount"].sum()
        .reset_index().sort_values("Amount", ascending=False)
    )
    top    = invest.head(5)
    others = pd.DataFrame({
        "Investment_Type": ["Others"],
        "Amount": [invest["Amount"].iloc[5:].sum()],
    })
    invest_final = pd.concat([top, others])

    fig4 = style_chart_executive(
        px.pie(invest_final, names="Investment_Type", values="Amount", hole=0.72,
               title="💰 Investment Type Distribution",
               color_discrete_sequence=[
                   "#1F3C88", "#2EC4B6", "#FF9F1C", "#6C63FF", "#00A8E8", "#B0BEC5"
               ])
    )
    fig4.update_traces(textposition="outside", textinfo="percent")
    fig4.update_layout(
        annotations=[dict(text=f"${total/1e9:.1f}B", x=0.5, y=0.5,
                          font_size=28, showarrow=False)]
    )

    # Dynamic insights panel
    top_city_name     = data.groupby("City")["Amount"].sum().idxmax()
    top_industry_name = data.groupby("Industry")["Amount"].sum().idxmax()
    top_type_name     = data.groupby("Investment_Type")["Amount"].sum().idxmax()

    insights = html.Div([
        html.H3("📊 Dynamic Insights",
                style={"fontSize": "21px", "color": "#1F3C88", "marginBottom": "10px"}),
        html.Ul([
            html.Li(f"Top City: {top_city_name} received the highest funding."),
            html.Li(f"Top Industry: {top_industry_name} attracted the most investment."),
            html.Li(f"Most common investment type: {top_type_name}."),
            html.Li(f"Total funding in selection: ${total:,.0f}."),
        ], style={"fontSize": "21px", "lineHeight": "1.8"}),
    ])

    executive_panel = html.Div([

        html.Div(
            kpis,
            style={"display": "grid",
                   "gridTemplateColumns": "repeat(4,1fr)",
                   "gap": "18px",
                   "marginBottom": "25px"},
        ),

        html.Div([
            html.Div(dcc.Graph(id="trend_chart",      figure=fig1,
                               style={"height": "420px"}),
                     style=CARD_STYLE, className="chart-card"),
            html.Div(dcc.Graph(id="industry_chart",   figure=fig2,
                               style={"height": "420px"}),
                     style=CARD_STYLE, className="chart-card"),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                  "gap": "18px", "marginBottom": "18px"}),

        html.Div([
            html.Div(dcc.Graph(id="city_chart",       figure=fig3,
                               style={"height": "420px"}),
                     style=CARD_STYLE, className="chart-card"),
            html.Div(dcc.Graph(id="investment_chart", figure=fig4,
                               style={"height": "420px"}),
                     style=CARD_STYLE, className="chart-card"),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                  "gap": "18px"}),

        html.Div(
            insights,
            style={"background": "white", "padding": "18px",
                   "borderRadius": "10px", "marginTop": "20px",
                   "boxShadow": "0 2px 6px rgba(0,0,0,0.08)"},
        ),

    ])

    return executive_panel, year, industry, city, investment


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(debug=True, port=8056)
