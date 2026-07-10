import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# -----------------------
# Load dataset
# -----------------------

df = pd.read_excel("data/Startup_Cleaned_Dataset_.xlsx")

# -----------------------
# Color palette
# -----------------------

colors = {
    "background": "#F5F7FB",
    "primary": "#1F3C88",
    "secondary": "#2EC4B6",
    "highlight": "#6C63FF",
    "accent": "#FF9F1C",
    "text": "#2B2B2B"
}

# -----------------------
# Initialize App
# -----------------------

app = Dash(__name__)

# -----------------------
# 1️⃣ Growth vs Profitability
# -----------------------

fig1 = px.scatter(
    df,
    x="Revenue Growth Rate (%)",
    y="Profit Margin (%)",
    color="Profit Margin (%)",
    title="Growth vs Profitability",
    color_continuous_scale=[colors["secondary"], colors["highlight"]]
)

fig1.add_vline(x=0, line_dash="dash")
fig1.add_hline(y=0, line_dash="dash")

# -----------------------
# 2️⃣ Funding Outliers
# -----------------------

fig2 = px.box(
    df,
    y="Amount in USD",
    title="Funding Outliers",
    color_discrete_sequence=[colors["accent"]]
)

# -----------------------
# 3️⃣ Funding by Stage (FIXED)
# -----------------------

stage_df = (
    df.groupby("Investment_Type_std")["Amount in USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3 = px.bar(
    stage_df,
    y="Investment_Type_std",
    x="Amount in USD",
    orientation="h",
    title="Funding by Stage (Top 10)",
    color_discrete_sequence=["#1F3C88"]  # Deep Blue
)

# -----------------------
# 4️⃣ Top Investors
# -----------------------

top_investors = (
    df.groupby("Investors_Name_Std")["Amount in USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_investors,
    y="Investors_Name_Std",
    x="Amount in USD",
    orientation="h",
    title="Top Investors by Funding",
    color_discrete_sequence=[colors["highlight"]]
)

# -----------------------
# Common Styling
# -----------------------

for fig in [fig1, fig2, fig3, fig4]:
    fig.update_layout(
        template="plotly_white",
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        title_x=0.5
    )

# -----------------------
# Layout
# -----------------------

app.layout = html.Div(

    style={
        "backgroundColor": colors["background"],
        "height": "100vh",
        "width": "100vw",
        "padding": "10px",
        "fontFamily": "Segoe UI",
        "color": colors["text"]
    },

    children=[

        # Title
        html.H3(
            "Advanced Insights Dashboard",
            style={
                "textAlign": "center",
                "color": colors["primary"],
                "marginBottom": "10px"
            }
        ),

        # Grid Layout
        html.Div(

            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gridTemplateRows": "1fr 1fr",
                "gap": "10px",
                "height": "90vh"
            },

            children=[

                dcc.Graph(figure=fig1, config={"displayModeBar": False}),
                dcc.Graph(figure=fig2, config={"displayModeBar": False}),
                dcc.Graph(figure=fig3, config={"displayModeBar": False}),
                dcc.Graph(figure=fig4, config={"displayModeBar": False})

            ]

        )

    ]

)

# -----------------------
# Run server
# -----------------------

if __name__ == "__main__":
    app.run(debug=True)