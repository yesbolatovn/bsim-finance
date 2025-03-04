from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from dashboards.views import get_financial_data

# Initialize Dash App
app = DjangoDash("FinancialDashboards", suppress_callback_exceptions=True)

# Dash Layout - Set to display all charts in a responsive layout
app.layout = html.Div([
    dcc.Store(id="project_id", storage_type="session"),
    dcc.Store(id="cycle_id", storage_type="session"),

    html.H1(id="dashboard-title", style={"text-align": "center"}),

    html.Div([
        html.Div([
            dcc.Graph(id="cost-structure", style={"height": "400px", "width": "48%"}),
            dcc.Graph(id="gross-profit", style={"height": "400px", "width": "48%"})
        ], style={"display": "flex", "justify-content": "space-between", "width": "100%"}),

        html.Div([
            dcc.Graph(id="net-income", style={"height": "400px", "width": "48%"}),
            dcc.Graph(id="financial-ratios", style={"height": "400px", "width": "48%"})
        ], style={"display": "flex", "justify-content": "space-between", "width": "100%"}),

    ], style={"width": "100%", "max-width": "1600px", "margin": "auto"})
])


@app.callback(
    [
        Output("dashboard-title", "children"),
        Output("cost-structure", "figure"),
        Output("gross-profit", "figure"),
        Output("net-income", "figure"),
        Output("financial-ratios", "figure"),
    ],
    [Input("project_id", "data"), Input("cycle_id", "data")]
)
def update_dashboard(project_id, cycle_id):
    print(f"DASH CALLBACK: Received Project ID = {project_id}, Cycle ID = {cycle_id}")

    if not project_id or not cycle_id:
        return "Financial Dashboards", {}, {}, {}, {}

    data = get_financial_data(project_id, cycle_id)
    print(f"DASH CALLBACK: Retrieved Financial Data: {data}")

    # Cost Structure Chart
    cost_structure_fig = go.Figure()
    cost_structure_fig.add_trace(go.Bar(x=data["years"], y=data["variable_costs"], name="Variable Costs", marker_color="blue"))
    cost_structure_fig.add_trace(go.Bar(x=data["years"], y=data["fixed_costs"], name="Fixed Costs", marker_color="red"))
    cost_structure_fig.update_layout(title="Cost Structure", xaxis_title="Fiscal Year", yaxis_title="Amount ($)", barmode="stack", height=400)

    # Gross Profit vs Revenue Chart
    gross_profit_fig = go.Figure()
    gross_profit_fig.add_trace(go.Bar(x=data["years"], y=data["revenue"], name="Revenue", marker_color="blue"))
    gross_profit_fig.add_trace(go.Bar(x=data["years"], y=data["gross_profit"], name="Gross Profit", marker_color="green"))
    gross_profit_fig.update_layout(title="Gross Profit vs Revenue", xaxis_title="Fiscal Year", yaxis_title="Amount ($)", height=400)

    # Net Income Chart
    net_income_fig = go.Figure()
    net_income_fig.add_trace(go.Scatter(x=data["years"], y=data["net_income"], mode="lines+markers", name="Net Income", marker_color="red"))
    net_income_fig.update_layout(title="Net Income After Tax", xaxis_title="Fiscal Year", yaxis_title="Amount ($)", height=400)

    # Financial Ratios Chart
    ratios_fig = go.Figure()
    ratios_fig.add_trace(go.Scatter(x=data["years"], y=data["operating_margin"], mode="lines+markers", name="Operating Margin", marker_color="blue"))
    ratios_fig.add_trace(go.Scatter(x=data["years"], y=data["net_profit_margin"], mode="lines+markers", name="Net Profit Margin", marker_color="red"))
    ratios_fig.update_layout(title="Financial Ratios", xaxis_title="Fiscal Year", yaxis_title="Percentage (%)", height=400)

    return (
        f"Financial Dashboards for Project {project_id} - Cycle {cycle_id}",
        cost_structure_fig,
        gross_profit_fig,
        net_income_fig,
        ratios_fig
    )
