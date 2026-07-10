#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ==============================
# IMPORT LIBRARIES
# ==============================

import pandas as pd
from dash import Dash, html, dcc, Input, Output, ctx
import plotly.express as px

# ==============================
# LOAD DATA
# ==============================

df = pd.read_excel("Startup_Cleaned_Dataset_.xlsx")

df = df.rename(columns={
    "Startup_Name": "Startup",
    "Industry_Vertical_Std": "Industry",
    "City_Location_Std": "City",
    "Investment_Type_std": "Investment_Type",
    "Investors_Name_Std": "Investor",
    "Amount in USD": "Amount"
})

df["Year"] = df["Year"].astype(str)

# ==============================
# DASH APP
# ==============================

app = Dash(__name__)

# ==============================
# DROPDOWN + HOVER CSS
# ==============================

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>Startup Funding Analysis Dashboard</title>
{%favicon%}
{%css%}

<style>

/* Dropdown Size */
.Select-control {
height:80px !important;
min-height:80px !important;
}

.Select-placeholder {
line-height:80px !important;
}

.Select-input {
height:80px !important;
}

.Select-value {
line-height:80px !important;
}

/* KPI Hover Animation */
.card-hover{
transition:all 0.3s ease;
}

.card-hover:hover{
transform:translateY(-6px);
box-shadow:0 12px 25px rgba(0,0,0,0.18) !important;
}

/* Chart Hover */
.chart-card{
transition:all 0.3s ease;
}

.chart-card:hover{
transform:translateY(-5px);
box-shadow:0 10px 20px rgba(0,0,0,0.15) !important;
}

/* Button Hover */
button:hover{
transform:scale(1.02);
transition:0.25s;
}

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
'''

# ==============================
# PAGE STYLE
# ==============================

PAGE_STYLE = {
    "backgroundColor": "#EEF2F7",
    "padding": "20px",
    "fontFamily": "Segoe UI",
    "maxWidth": "4000px",
    "margin": "auto"
}

CARD_STYLE = {
    "background": "white",
    "borderRadius": "12px",
    "boxShadow": "0 3px 10px rgba(0,0,0,0.08)",
    "padding": "15px",
    "border": "1px solid #E6E6E6",
    "textAlign": "center"
}

# ==============================
# CHART STYLE FUNCTION
# ==============================

def style_chart(fig):

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI", size=18),
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 30}
        },
        margin=dict(l=10, r=10, t=60, b=10)
    )

    return fig

# ==============================
# LAYOUT
# ==============================

app.layout = html.Div(style=PAGE_STYLE, children=[

html.H1(
"🏢 Startup Funding Analysis Dashboard",
style={
"textAlign":"center",
"color":"white",
"fontSize":"40px",
"fontWeight":"700",
"padding":"20px",
"marginBottom":"25px",
"borderRadius":"10px",
"background":"linear-gradient(90deg,#1F3C88,#6C63FF)"
}

),

# ==============================
# SIDEBAR + DASHBOARD
# ==============================

html.Div([

# SIDEBAR
html.Div([

html.H3("Filters",style={"color":"#1F3C88","marginBottom":"25px","fontSize":"26px","fontWeight":"800"}),

html.Div([
html.Label("📅 Year",style={"fontSize":"25px","fontWeight":"600","marginBottom":"6px"}),
dcc.Dropdown(
id="year",
options=[{"label":i,"value":i} for i in sorted(df["Year"].unique())],
multi=True,
style={"fontSize":"22px"}
)
],style={"marginBottom":"30px","flexGrow":"1"}),

html.Div([
html.Label("🏭 Industry",style={"fontSize":"25px","fontWeight":"600","marginBottom":"6px"}),
dcc.Dropdown(
id="industry",
options=[{"label":i,"value":i} for i in sorted(df["Industry"].dropna().unique())],
multi=True,
style={"fontSize":"22px"}
)
],style={"marginBottom":"30px","flexGrow":"1"}),

html.Div([
html.Label("📍City",style={"fontSize":"25px","fontWeight":"600","marginBottom":"6px"}),
dcc.Dropdown(
id="city",
options=[{"label":i,"value":i} for i in sorted(df["City"].dropna().unique())],
multi=True,
style={"fontSize":"22px"}
)
],style={"marginBottom":"30px","flexGrow":"1"}),

html.Div([
html.Label("💰 Investment Type",style={"fontSize":"25px","fontWeight":"600","marginBottom":"6px"}),
dcc.Dropdown(
id="investment",
options=[{"label":i,"value":i} for i in sorted(df["Investment_Type"].dropna().unique())],
multi=True,
style={"fontSize":"22px"}
)
],style={"marginBottom":"30px","flexGrow":"1"}),

html.Button(
"Reset Filters",
id="reset-btn",
n_clicks=0,
style={
"background":"#FF9F1C",
"color":"white",
"border":"none",
"borderRadius":"8px",
"cursor":"pointer",
"width":"100%",
"fontSize":"28px",
"fontWeight":"650",
"height":"100px",
"boxShadow":"0 4px 10px rgba(0,0,0,0.15)"
}
)

],

style={
"width":"18%",
"background":"white",
"padding":"20px",
"borderRadius":"10px",
"boxShadow":"0 2px 6px rgba(0,0,0,0.08)",
"display":"flex",
"flexDirection":"column",
"justifyContent":"space-between",
"minHeight":"100%"
}

),

# MAIN DASHBOARD
html.Div([

html.Div(
id="kpi-cards",
style={
"display":"grid",
"gridTemplateColumns":"repeat(4,1fr)",
"gap":"18px",
"marginBottom":"25px"
}
),

html.Div([

html.Div(
dcc.Graph(id="trend_chart",style={"height":"420px"}),
style=CARD_STYLE,
className="chart-card"
),

html.Div(
dcc.Graph(id="industry_chart",style={"height":"420px"}),
style=CARD_STYLE,
className="chart-card"    
)

],
style={
"display":"grid",
"gridTemplateColumns":"1fr 1fr",
"gap":"18px",
"marginBottom":"18px"
}
),

html.Div([

html.Div(
dcc.Graph(id="city_chart",style={"height":"420px"}),
style=CARD_STYLE,
className="chart-card"    
),

html.Div(
dcc.Graph(id="investment_chart",style={"height":"420px"}),
style=CARD_STYLE,
className="chart-card"    
)

],
style={
"display":"grid",
"gridTemplateColumns":"1fr 1fr",
"gap":"18px"
}
),

html.Div(
id="insights_panel",
style={
"background":"white",
"padding":"18px",
"borderRadius":"10px",
"marginTop":"20px",
"boxShadow":"0 2px 6px rgba(0,0,0,0.08)"
}
)

],

style={"width":"80%","marginLeft":"20px"})

],
style={"display":"flex"})

])

# ==============================
# CALLBACK
# ==============================

@app.callback(

Output("kpi-cards","children"),
Output("trend_chart","figure"),
Output("industry_chart","figure"),
Output("city_chart","figure"),
Output("investment_chart","figure"),
Output("insights_panel","children"),

Output("year","value"),
Output("industry","value"),
Output("city","value"),
Output("investment","value"),

Input("year","value"),
Input("industry","value"),
Input("city","value"),
Input("investment","value"),
Input("reset-btn","n_clicks")

)

def update_dashboard(year,industry,city,investment,reset):

    trigger = ctx.triggered_id

    if trigger == "reset-btn":
        year=None
        industry=None
        city=None
        investment=None

    data=df.copy()

    if year:
        data=data[data["Year"].isin(year)]

    if industry:
        data=data[data["Industry"].isin(industry)]

    if city:
        data=data[data["City"].isin(city)]

    if investment:
        data=data[data["Investment_Type"].isin(investment)]

    total=data["Amount"].sum()
    startups=data["Startup"].nunique()
    avg=data["Amount"].mean()
    investors=data["Investor"].nunique()

    kpis=[

html.Div([
html.P("💰 Total Funding",style={"fontSize":"30px","fontWeight":"600"}),
html.H3(f"${total:,.0f}",style={"fontSize":"36px","color":"#1F3C88"})
],style={**CARD_STYLE,"borderLeft":"6px solid #1F3C88"},className="card-hover"),

html.Div([
html.P("🏢 Startups",style={"fontSize":"30px","fontWeight":"600"}),
html.H3(startups,style={"fontSize":"36px","color":"#2EC4B6"})
],style={**CARD_STYLE,"borderLeft":"6px solid #2EC4B6"},className="card-hover"),

html.Div([
html.P("📈 Average Funding",style={"fontSize":"30px","fontWeight":"600"}),
html.H3(f"${avg:,.0f}",style={"fontSize":"36px","color":"#FF9F1C"})
],style={**CARD_STYLE,"borderLeft":"6px solid #FF9F1C"},className="card-hover"),

html.Div([
html.P("🤝 Investors",style={"fontSize":"30px","fontWeight":"600"}),
html.H3(investors,style={"fontSize":"36px","color":"#6C63FF"})
],style={**CARD_STYLE,"borderLeft":"6px solid #6C63FF"},className="card-hover")

]

    trend=data.groupby("Year")["Amount"].sum().reset_index()

    fig1=style_chart(
        px.line(
            trend,
            x="Year",
            y="Amount",
            markers=True,
            title="📈 Funding Trend Over Time",
            color_discrete_sequence=["#1F3C88"]
        )
    )
    fig1.update_traces(
        hovertemplate="<b>%{x}</b><br>Funding: %{y:$,.0f}<extra></extra>",
        line=dict(width=5),
        marker=dict(size=10)
    )

    industry_chart=data.groupby("Industry")["Amount"].sum().nlargest(10).reset_index()

    max_industry=industry_chart["Amount"].max()

    industry_chart["color"]=industry_chart["Amount"].apply(
        lambda x:"#FF9F1C" if x==max_industry else "#6C63FF"
    )

    fig2=style_chart(px.bar(
        industry_chart,
        x="Amount",
        y="Industry",
        orientation="h",
        title="🏭 Top Industries by Funding",
        color="color",
        color_discrete_map="identity"
    ))
    fig2.update_traces(
    hovertemplate="<b>%{y}</b><br>Funding: %{x:$,.0f}<extra></extra>"
    )
    fig2.update_traces(marker_cornerradius=8)

    fig2.update_yaxes(
    title_standoff=25,
    ticklabelposition="outside",
    ticklabelstandoff=12
    )

    city_chart=data.groupby("City")["Amount"].sum().nlargest(10).reset_index()

    max_city=city_chart["Amount"].max()

    city_chart["color"]=city_chart["Amount"].apply(
        lambda x:"#FF9F1C" if x==max_city else "#2EC4B6"
    )

    fig3=style_chart(px.bar(
        city_chart,
        x="City",
        y="Amount",
        title="📍 Funding by City",
        color="color",
        color_discrete_map="identity"
    ))
    fig3.update_traces(
    hovertemplate="<b>%{x}</b><br>Funding: %{y:$,.0f}<extra></extra>"
    )
    fig3.update_traces(marker_cornerradius=8)

    invest=data.groupby("Investment_Type")["Amount"].sum().reset_index()
    invest=invest.sort_values("Amount",ascending=False)

    top=invest.head(5)

    others=pd.DataFrame({
        "Investment_Type":["Others"],
        "Amount":[invest["Amount"][5:].sum()]
    })

    invest_final=pd.concat([top,others])

    fig4=px.pie(
        invest_final,
        names="Investment_Type",
        values="Amount",
        hole=0.72,
        title="💰 Investment Type Distribution",
        color_discrete_sequence=[
        "#1F3C88","#2EC4B6","#FF9F1C","#6C63FF","#00A8E8","#B0BEC5"]
    )

    fig4.update_traces(textposition="outside",textinfo="percent")

    fig4.update_layout(
        annotations=[dict(
            text=f"${total/1e9:.1f}B",
            x=0.5,
            y=0.5,
            font_size=28,
            showarrow=False
        )]
    )

    fig4=style_chart(fig4)

    top_city=data.groupby("City")["Amount"].sum().idxmax()
    top_industry=data.groupby("Industry")["Amount"].sum().idxmax()
    top_type=data.groupby("Investment_Type")["Amount"].sum().idxmax()

    insights=html.Div([

html.H3(
"📊 Dynamic Insights",
style={"fontSize":"21px","color":"#1F3C88","marginBottom":"10px"}
),

html.Ul([
html.Li(f"Top City: {top_city} received the highest funding."),
html.Li(f"Top Industry: {top_industry} attracted the most investment."),
html.Li(f"Most common investment type: {top_type}."),
html.Li(f"Total funding in selection: ${total:,.0f}.")
],style={"fontSize":"21px","lineHeight":"1.8"})

])

    return kpis,fig1,fig2,fig3,fig4,insights,year,industry,city,investment


# ==============================
# RUN APP
# ==============================

if __name__=="__main__":
    app.run(debug=True,port=8056)


# In[ ]:




