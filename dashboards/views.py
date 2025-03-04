from django.shortcuts import render, get_object_or_404
from b_sim.models import Project, Cycle, SalesProjection, Employee, Rent, Utility, Debt, MarketingEntry, Tax
from django.db.models import Sum
from decimal import Decimal

def financial_dashboards_view(request, project_id, cycle_id):
    """View to render the financial dashboards page with Dash integration."""

    print(f"DEBUG: Received in Django View - Project {project_id}, Cycle {cycle_id}")

    project = get_object_or_404(Project, id=project_id)
    cycle = get_object_or_404(Cycle, id=cycle_id)

    context = {
        "project": project,
        "cycle": cycle,
        "project_id": project_id,
        "cycle_id": cycle_id,
    }

    return render(request, "dashboards/financial_dashboards.html", context)


def safe_decimal(value):
    """ Convert float to Decimal to prevent summation errors. """
    return Decimal(str(value)) if value is not None else Decimal(0)

def decimal_to_float(data_dict):
    """ Convert all Decimal values to float, but exclude 'years' key. """
    return {k: [float(v) for v in values] if k != "years" else values for k, values in data_dict.items()}

def get_financial_data(project_id, cycle_id):
    """Fetch and return financial data formatted for Plotly."""
    years = ["FY-1", "FY-2", "FY-3"]
    variable_costs, fixed_costs, revenue, gross_profit, net_income, operating_margin, net_profit_margin = [], [], [], [], [], [], []

    for fy in range(1, 4):
        sales_data = SalesProjection.objects.filter(project_id=project_id, cycle_id=cycle_id, fy=fy)

        net_sales = safe_decimal(sales_data.aggregate(total=Sum("revenue"))["total"])
        cost_of_sales = safe_decimal(sales_data.aggregate(total=Sum("expense"))["total"])
        gross_profit_value = net_sales - cost_of_sales

        fixed_costs_data = {
            "rent": safe_decimal(Rent.objects.filter(project_id=project_id, cycle_id=cycle_id).aggregate(total=Sum(f"rent_payment_fy{fy}"))["total"]),
            "salaries": safe_decimal(Employee.objects.filter(project_id=project_id, cycle_id=cycle_id).aggregate(total=Sum(f"employee_budget_fy{fy}"))["total"]),
            "utilities": safe_decimal(Utility.objects.filter(project_id=project_id, cycle_id=cycle_id).aggregate(total=Sum(f"utility_budget_fy{fy}"))["total"]),
            "marketing": safe_decimal(MarketingEntry.objects.filter(project_id=project_id, cycle_id=cycle_id).aggregate(total=Sum(f"payment_fy{fy}_value"))["total"]),
            "loan_payments": safe_decimal(Debt.objects.filter(project_id=project_id, cycle_id=cycle_id).aggregate(total=Sum(f"debt_payment_fy{fy}"))["total"]),
            "depreciation": safe_decimal(7500 if fy == 1 else 14250 if fy == 2 else 12825),
        }

        total_fixed_costs = sum(fixed_costs_data.values())
        total_expenses = cost_of_sales + total_fixed_costs
        operating_income = gross_profit_value - total_fixed_costs
        tax_rate = Decimal("0.35")
        tax_expense = operating_income * tax_rate if operating_income > 0 else Decimal(0)
        net_income_value = operating_income - tax_expense

        operating_margin_value = (operating_income / net_sales * 100) if net_sales > 0 else Decimal(0)
        net_profit_margin_value = (net_income_value / net_sales * 100) if net_sales > 0 else Decimal(0)

        variable_costs.append(cost_of_sales)
        fixed_costs.append(total_fixed_costs)
        revenue.append(net_sales)
        gross_profit.append(gross_profit_value)
        net_income.append(net_income_value)
        operating_margin.append(operating_margin_value)
        net_profit_margin.append(net_profit_margin_value)

    data = {
        "years": years,
        "variable_costs": variable_costs,
        "fixed_costs": fixed_costs,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "net_income": net_income,
        "operating_margin": operating_margin,
        "net_profit_margin": net_profit_margin,
    }

    return decimal_to_float(data)  # Convert Decimal to float before returning
