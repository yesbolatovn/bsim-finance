import scipy
import scipy.stats as ss
import traceback

import random
import string

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.patches import FancyArrow

import seaborn as sns
from io import BytesIO
import base64

from pprint import pprint

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import MarketingEntry, Product, TargetMarketSize, SalesProjection
from .models import Employee, Utility, Rent, Tax, FinancialMarketIndicator, Debt
from .models import Project, Cycle, FinancialManagement, ProjectStartSettings

from .forms import ProjectStartForm, CustomPasswordChangeForm, CycleComparisonForm, CycleDeleteForm, UploadUsersForm
from .forms import MarketingEntryForm, TargetMarketSizeForm, SalesProjectionForm, ProductForm, EmployeeForm
from .forms import UtilityForm, RentForm, TaxForm, FMIForm, TargetMarketSizeForm, ProjectForm, CycleForm, DebtForm

from django.views.decorators.http import require_POST

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from django.db.models import Sum

from decimal import Decimal

from django.contrib.auth.decorators import user_passes_test
from .forms import ProjectUserForm

from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.contrib import messages

from django.contrib.auth.hashers import make_password

import csv
from django.http import HttpResponse

# optimization
from scipy.optimize import minimize
from django.views.decorators.csrf import csrf_exempt
import json


def replace_none_with_zero(value):
    return 0 if value is None else value


def safe_division(numerator, denominator):
    try:
        numerator = float(numerator)
        denominator = float(denominator)
        if denominator != 0:
            return numerator / denominator
        else:
            return None
    except (ValueError, TypeError):
        return None


def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username is not already taken
        if not User.objects.filter(username=username).exists():
            # Create a new user with the provided username and password
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Log the user in after successful signup
            user = authenticate(request, username=username, password=password)
            login(request, user)

            return redirect('signin_page')  # Redirect to the dashboard page after signup and login

        else:
            error_message = 'Username already taken. Please choose a different username.'

            context = {
                'error_message': error_message
            }

            return render(
                request,
                'signup_page.html',
                context
            )

    return render(request, 'signup_page.html')


def success(request):
    context = {
        'user': request.user,
    }
    return render(request, 'success.html', context=context)


def is_admin(user):
    return user.is_superuser


def signin_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user with provided username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User credentials are valid, log the user in
            login(request, user)
            # return redirect('home_page')  # Redirect to the dashboard page after login
            return redirect('project_dashboard')

    return render(
        request,
        'signin_page.html'
    )


def signout_page(request):
    logout(request)
    return redirect('signin_page')


@user_passes_test(is_admin)
def change_password_as_admin(request):
    password_changed = False
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password1']

            try:
                user = User.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()
                password_changed = True
                messages.success(request, f'Password for {username} has been changed successfully.')
            except User.DoesNotExist:
                password_changed = False
                messages.error(request, 'Invalid username.')
    else:
        form = CustomPasswordChangeForm()

    return render(request, 'change_password.html', {'form': form, 'password_changed': password_changed})


def change_password(request):
    password_changed = False
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']

            user = authenticate(username=username, password=old_password)

            if user is not None:
                user.password = make_password(new_password)
                user.save()
                password_changed = True
            else:
                password_changed = False
                messages.error(request, 'Invalid username or old password.')
    else:
        form = CustomPasswordChangeForm()

    return render(request, 'change_password.html', {'form': form, 'password_changed': password_changed})


@login_required
def project_dashboard(request):
    user_projects = request.user.projects.all()

    is_super_user = is_admin(request.user)

    context = {
        'projects': user_projects,
        'superuser': is_super_user,
    }

    return render(
        request,
        'project_setup/project_dashboard.html',
        context
    )


@user_passes_test(is_admin)
def manage_project_users(request, project_id=None):
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None

    if request.method == 'POST':
        form = ProjectUserForm(request.POST, project=project)
        if form.is_valid():
            users = form.cleaned_data['users']
            if project:
                if 'add_users' in request.POST:
                    project.users.add(*users)
                elif 'remove_users' in request.POST:
                    project.users.remove(*users)
            else:
                project_name = request.POST.get('project_name')
                project = Project.objects.create(project_name=project_name)
                project.users.add(*users)
                instantiate_project_start(project)
            return redirect('manage_project_users', project_id=project.id)
    else:
        form = ProjectUserForm(project=project)

    context = {
        'form': form,
        'project': project,
        'request_function': "manage_project_users",
    }

    return render(
        request,
        'admin_utils/manage_project_users.html',
        context
    )


@user_passes_test(is_admin)
def create_project(request):
    project = None

    if request.method == 'POST':
        form = ProjectUserForm(request.POST, project=project)
        if form.is_valid():
            users = form.cleaned_data['users']
            if project:
                if 'add_users' in request.POST:
                    project.users.add(*users)
                elif 'remove_users' in request.POST:
                    project.users.remove(*users)
            else:
                project_name = request.POST.get('project_name')
                project = Project.objects.create(project_name=project_name)
                project.users.add(*users)
                instantiate_project_start(project)
            return redirect('create_project')
    else:
        form = ProjectUserForm(project=project)

    context = {
        'form': form,
        'project': project,
        'request_function': "create_project",
    }

    return render(
        request,
        'admin_utils/manage_project_users.html',
        context
    )


def project_home(request):
    pk = request.session['current_project_id']

    project_details = Project.objects.get(pk=pk)

    default_cycle_id = None
    default_cycle = Cycle.objects.filter(project=project_details)
    if default_cycle:
        default_cycle_id = default_cycle.first().id

    request.session['current_cycle_id'] = default_cycle_id

    project_start_settings = ProjectStartSettings.objects.get(project=pk)
    show_cycle_dashboard = False
    if not project_start_settings.is_editable:
        show_cycle_dashboard = True

    context = {
        'project': project_details,
        'show_cycle_dashboard': show_cycle_dashboard,
    }

    return render(
        request,
        'project_setup/project_home.html',
        context
    )


def cycle_home(request):
    pk = request.session['current_cycle_id']

    current_cycle = Cycle.objects.get(pk=pk)
    project = current_cycle.project

    context = {
        'cycle': current_cycle,
        'project' : current_cycle.project,
        'show_project_navbar': True,
    }

    return render(
        request,
        'project_setup/cycle_setup/cycle_home.html',
        context
    )


def sim_nav_page(request):
    context = {
        'show_project_navbar': False,
    }

    return render(
        request,
        'project_setup/sim_nav.html',
        context
    )


def help_page(request):
    context = {
        'show_project_navbar': False,
    }
    return render(
        request,
        'resources/help_page.html',
        context
    )


def how_to_play(request):
    context = {
        'show_project_navbar': False,
    }
    return render(
        request,
        'resources/how_to_play/how_to_play.html',
        context
    )


def copy_data_from_underlying_cycle(new_cycle, underlying_cycle):
    def duplicate_products_and_create_mapping(underlying_cycle, new_cycle):
        product_mapping = {}
        original_products = Product.objects.filter(cycle=underlying_cycle)
        for product in original_products:
            original_product_id = product.pk
            product.pk = None  # Reset PK to create a new instance
            product.cycle = new_cycle  # Assign to the new cycle
            product.save()  # Save the new product
            product_mapping[original_product_id] = product  # Map old ID to new product instance
        return product_mapping

    def copy_data_with_product_mapping(new_cycle, underlying_cycle, product_mapping):
        for old_product_id, new_product in product_mapping.items():
            # Duplicate TargetedMarketSize entries
            market_sizes = TargetMarketSize.objects.filter(product_id=old_product_id, cycle=underlying_cycle)
            for size in market_sizes:
                size.pk = None  # Reset PK
                size.product = new_product  # Link to new product
                size.cycle = new_cycle  # Assign to the new cycle
                size.save()  # Save the new market size

            # Duplicate SalesProjection entries
            sales_projections = SalesProjection.objects.filter(product_id=old_product_id, cycle=underlying_cycle)
            for projection in sales_projections:
                projection.pk = None  # Reset PK to create a new instance
                projection.product = new_product  # Link to the new product instance
                projection.cycle = new_cycle  # Assign to the new cycle
                projection.save()  # Save the new projection

    tables = [
        MarketingEntry, Utility, Employee, Debt, Rent, Tax, FinancialMarketIndicator,
    ]

    # Duplicate products and get a mapping from old product IDs to new product instances
    product_mapping = duplicate_products_and_create_mapping(underlying_cycle, new_cycle)

    # Use the product mapping to correctly copy SalesProjection and TargetedMarketSize entries
    copy_data_with_product_mapping(new_cycle, underlying_cycle, product_mapping)

    for table in tables:
        entries = table.objects.filter(cycle=underlying_cycle)
        for entry in entries:
            entry.pk = None
            entry.cycle = new_cycle
            entry.save()


@login_required
def cycle_dashboard(request):
    current_project_id = request.session.get('current_project_id')
    if not current_project_id:
        # Redirect to project selection if no project is currently selected
        return redirect('project_dashboard')

    try:
        current_project = Project.objects.get(id=current_project_id)
    except Project.DoesNotExist:
        # Handle the case where the project does not exist
        return redirect('project_dashboard')

    cycles = current_project.cycles.all()

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)

    if request.method == 'POST':
        form = CycleForm(request.POST, project_id=current_project.id)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.project = current_project

            underlying_cycle_id = form.cleaned_data.get('underlying_cycle')

            # Now save the cycle after potentially getting the underlying cycle
            cycle.save()
            form.save_m2m()  # If there are many-to-many fields that need saving

            if underlying_cycle_id:
                # Function to copy data from the selected underlying cycle to the new cycle
                copy_data_from_underlying_cycle(cycle, underlying_cycle_id)

            return redirect('cycle_dashboard')
    else:
        form = CycleForm(project_id=current_project.id)

    context = {
        'current_project': current_project,
        'cycles': cycles,
        'form': form,
    }

    return render(request, 'project_setup/cycle_setup/cycle_dashboard.html', context)


def project_start_display(request):
    current_project_id = request.session.get('current_project_id')
    project = get_object_or_404(Project, id=current_project_id)

    project_start_settings = ProjectStartSettings.objects.get(project=project)

    csf = [
        ["CSF 1", "Introducing an individually controlled brand (utilization in %)", "%",
         "",
         project_start_settings.brand_utilization_fy1 * 100,
         project_start_settings.brand_utilization_fy2 * 100,
         project_start_settings.brand_utilization_fy3 * 100,
         project_start_settings.brand_utilization_total * 100],
        ["CSF 2", "Retention of critical technology personnel", "number", "",
         project_start_settings.tech_personnel_retention_fy1,
         project_start_settings.tech_personnel_retention_fy2,
         project_start_settings.tech_personnel_retention_fy3, ""],
        ["CSF 3", "Retention of critical marketing personnel", "number", "",
         project_start_settings.marketing_personnel_retention_fy1,
         project_start_settings.marketing_personnel_retention_fy2,
         project_start_settings.marketing_personnel_retention_fy3, ""],
    ]

    kpi = [
        [("KPI 1", 2), "Actual size of the local market", "units",
         project_start_settings.actual_market_size_fy0, "", "", "", ""],
        ["Increase in size of the local market", "multiplier", "",
         project_start_settings.multiplier_fy1,
         project_start_settings.multiplier_fy2,
         project_start_settings.multiplier_fy3, ""],

        ["KPI 2",
         "Number of customers- existing business",
         "customers",
         project_start_settings.number_of_customers, "",
         "", "", ""],

        ["KPI 3", "Average consumption per existing customer", "pints",
         project_start_settings.average_consumption_per_customer, "", "", "", ""],

        [("KPI 4", 2), ("Size of the penetrated market - without new project", 2), "%", "",
         project_start_settings.market_size_without_project_fy1,
         project_start_settings.market_size_without_project_fy2,
         project_start_settings.market_size_without_project_fy3, ""],
        ["units",
         project_start_settings.market_size_without_project_fy0_unit,
         project_start_settings.market_size_without_project_fy1_unit,
         project_start_settings.market_size_without_project_fy2_unit,
         project_start_settings.market_size_without_project_fy3_unit,
         project_start_settings.market_size_without_project_unit_total],

        ["KPI 5", "Projected increase of the penetrated market - with new project", "%", "",
         "", "", "",
         project_start_settings.projected_increase_with_project],

        [("KPI 6", 2), "Projected structure of the annual sales, new penetr. market", "%", "",
         project_start_settings.projected_annual_sales_fy1,
         project_start_settings.projected_annual_sales_fy2,
         project_start_settings.projected_annual_sales_fy3, ""],
        ["Projected sales, new brand", "units", "",
         project_start_settings.projected_new_brand_sales_fy1,
         project_start_settings.projected_new_brand_sales_fy2,
         project_start_settings.projected_new_brand_sales_fy3,
         project_start_settings.projected_new_brand_sales_total],

        [("KPI 7", 5), ("Projected consumption in the existing business, new brand only", 2), "%", "",
         project_start_settings.projected_consumption_new_brand_fy1,
         project_start_settings.projected_consumption_new_brand_fy2,
         project_start_settings.projected_consumption_new_brand_fy3, ""],
        ["units", "",
         project_start_settings.projected_consumption_new_brand_fy1_unit,
         project_start_settings.projected_consumption_new_brand_fy2_unit,
         project_start_settings.projected_consumption_new_brand_fy3_unit,
         project_start_settings.projected_consumption_new_brand_unit_total],
        ["Projected beer consumption (new brand % of all)", "%", "",
         project_start_settings.projected_beer_consumption_fy1 * 100,
         project_start_settings.projected_beer_consumption_fy2 * 100,
         project_start_settings.projected_beer_consumption_fy3 * 100, ""],
        [("Wholesale distribution (new brand)", 2), "%", "",
         project_start_settings.wholesale_distribution_fy1,
         project_start_settings.wholesale_distribution_fy2,
         project_start_settings.wholesale_distribution_fy3,
         project_start_settings.wholesale_distribution_total * 100],
        ["units", "",
         project_start_settings.wholesale_distribution_fy1_unit,
         project_start_settings.wholesale_distribution_fy2_unit,
         project_start_settings.wholesale_distribution_fy3_unit,
         project_start_settings.wholesale_distribution_unit_total],

        ["KPI 8", "Capacity of the new technology (max units/year)", "units", "",
         project_start_settings.new_technology_capacity,
         project_start_settings.new_technology_capacity,
         project_start_settings.new_technology_capacity, ""],
    ]

    if request.method == 'POST' and 'finalize' in request.POST:
        project_start_settings.is_editable = False
        project_start_settings.save()
        instantiate_marketing_mgmt(request)
        return redirect('project_dashboard')

    context = {
        'csf': csf,
        'kpi': kpi,
        'project_start_settings': project_start_settings
    }

    return render(
        request,
        'project_start/project_start_display.html',
        context
    )


def project_start(request):
    current_project_id = request.session.get('current_project_id')
    project = get_object_or_404(Project, id=current_project_id)

    project_start_settings = get_object_or_404(ProjectStartSettings, project_id=current_project_id)

    if not project_start_settings.is_editable:
        return redirect("project_start_display")

    # Attempt to get the ProjectStartSettings for the given project, or create it if it doesn't exist
    project_start_settings, created = ProjectStartSettings.objects.get_or_create(project=project)

    if request.method == 'POST':
        # Instantiate the form with the POST data and the ProjectStartSettings instance
        form = ProjectStartForm(request.POST, instance=project_start_settings)
        if form.is_valid():
            project_start_settings.save()
            return redirect('project_start_display')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
    else:
        # Instantiate the form with the existing ProjectStartSettings instance
        form = ProjectStartForm(instance=project_start_settings)

    # Render the form with the project and form context
    return render(request, 'project_start/project_start_form.html', {'form': form, 'project': project})


def instantiate_project_start(project):
    # Use get_or_create to avoid duplicate entries
    project_start_entry, created = ProjectStartSettings.objects.get_or_create(project=project)

    # Check if a new entry was created
    if created:
        project_start_entry.save()

    return project_start_entry


def instantiate_marketing_mgmt(request):
    current_project_id = request.session.get('current_project_id')
    project = get_object_or_404(Project, id=current_project_id)

    marketing_cycle = Cycle.objects.create(
        project=project,
        cycle_name='Marketing',
        underlying_cycle=None
    )

    default_products = [
        {"product_id": "1", "product_name": "Pilsner", "material_cost": 0.35, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "2", "product_name": "Bavarian Lager", "material_cost": 0.35, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "3", "product_name": "Light Wheat", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "4", "product_name": "Red Wheat", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "5", "product_name": "Pale Ale", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "6", "product_name": "Nut Brown Ale", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 0.8, "product_distribution": "retail"},
        {"product_id": "7", "product_name": "Bock Dark", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 1, "product_distribution": "wholesale"},
        {"product_id": "8", "product_name": "Stout", "material_cost": 0.33, "labor_cost": 0.1,
         "other_cost": 0.15, "price": 4, "units": 1, "cutoff": 1, "product_distribution": "wholesale"},
    ]

    for prod in default_products:
        cycle = marketing_cycle
        product = Product.objects.create(
            cycle=cycle,
            project=project,
            product_id=prod["product_id"],
            product_name=prod["product_name"],
            product_distribution=prod["product_distribution"],  # Default distribution, can be changed as needed
            material_cost=prod["material_cost"],
            labor_cost=prod["labor_cost"],
            other_cost=prod["other_cost"],
            price=prod["price"],
            cutoff=prod["cutoff"],
            units=prod["units"],
        )

        if prod["product_distribution"] == "retail":
            tms_pct = 16.67
        if prod["product_distribution"] == "wholesale":
            tms_pct = 50

        # Create TargetMarketSize entries for each FY
        for fy in [1, 2, 3]:
            TargetMarketSize.objects.create(
                product=product,
                cycle=cycle,
                project=project,
                fy=fy,
                tms_pct=tms_pct,  # Initialize default value
            )

        # Create SalesProjection entries for each FY and each month
        for fy in [1, 2, 3]:
            for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                SalesProjection.objects.create(
                    product=product,
                    cycle=cycle,
                    project=project,
                    fy=fy,
                    month=month,
                    projection=8.3,  # Initialize
                )

    instantiate_financial_mgmt(marketing_cycle, project)


def instantiate_financial_mgmt(cycle_id, project_id):
    employee_entries = FinancialManagement.objects.filter(fin_type='employee')
    utility_entries = FinancialManagement.objects.filter(fin_type='utility')
    rent_entries = FinancialManagement.objects.filter(fin_type='rent')
    tax_entries = FinancialManagement.objects.filter(fin_type='tax')
    fmi_entries = FinancialManagement.objects.filter(fin_type='fmi')

    for entry in employee_entries:
        user_employees = Employee.objects.create(
            cycle=cycle_id,
            project=project_id,
            employee_position=entry.fin_entry,
        )
        user_employees.save()

    for entry in utility_entries:
        user_utility = Utility.objects.create(
            cycle=cycle_id,
            project=project_id,
            utility_name=entry.fin_entry,
        )
        user_utility.save()

    for entry in rent_entries:
        user_rent = Rent.objects.create(
            cycle=cycle_id,
            project=project_id,
            rent_name=entry.fin_entry,
        )
        user_rent.save()

    for entry in tax_entries:
        user_tax = Tax.objects.create(
            cycle=cycle_id,
            project=project_id,
            tax_type=entry.fin_entry,
        )
        user_tax.save()

    for entry in fmi_entries:
        user_fmi = FinancialMarketIndicator.objects.create(
            cycle=cycle_id,
            project=project_id,
            name=entry.fin_entry,
        )
        user_fmi.save()


def perform_adhoc(request):
    upgrades_to = [
        ()
    ]


@login_required
def select_project(request, pk):
    request.session['current_project_id'] = pk

    return redirect('project_home')


@login_required
def select_cycle(request, pk):
    request.session['current_cycle_id'] = pk
    return redirect('cycle_home')


@login_required
def innovation_management(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)
    products = Product.objects.filter(cycle=current_cycle)

    spl_offer = products[:1]

    context = {
        'current_cycle': current_cycle,
        'underlying_cycle': current_cycle.underlying_cycle,
        'products': products,
        'show_project_navbar': True,
        'spl_offer': spl_offer,
    }

    return render(
        request,
        'innovation_management/innovation_management.html',
        context
    )


@login_required
def operations_management(request):
    def prepare_tms_data(products, cycle):
        product_data = []
        for product in products:
            tms_data = list(
                product.targeted_market_size.filter(cycle=cycle).values('fy', 'tms_pct', 'tms_value', 'cycle'))

            # Initialize default TMS data for new products
            default_tms_data = {'FY1': None, 'FY2': None, 'FY3': None}
            # Populate with actual data if available
            tms_dict = {fy: tms for fy, tms in default_tms_data.items()}
            for tms in tms_data:
                tms_dict[tms['fy']] = tms

            product_info = {
                'product_pk': product.product_pk,
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_distribution': product.product_distribution,
                'cycle': cycle,
                'tms': tms_dict,
            }
            product_data.append(product_info)
        return product_data

    def prepare_sales_projections(product_list, cycle):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        product_data_by_fy = {fy: [] for fy in financial_years}

        for product in product_list:
            projections_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            demand_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            tank_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            supply_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            revenue_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            expense_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            contribution_by_fy = {fy: {month: None for month in months} for fy in financial_years}

            product_price = product.price
            variable_cost = product.material_cost + product.labor_cost + product.other_cost

            for projection in product.sales_projection.filter(cycle=cycle):
                if projection.fy in projections_by_fy:
                    projections_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.projection)
                    demand_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.demand_quantity)
                    tank_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.tank_quantity)
                    supply_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.supply_quantity)
                    revenue_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.revenue)
                    expense_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.expense)
                    contribution_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.contribution)

            for fy in financial_years:
                total_projection = replace_none_with_zero(sum(filter(None, projections_by_fy[fy].values())))
                total_demand_quantity = replace_none_with_zero(sum(filter(None, demand_quantity_by_fy[fy].values())))
                total_tank_quantity = replace_none_with_zero(sum(filter(None, tank_quantity_by_fy[fy].values())))
                total_supply_quantity = replace_none_with_zero(sum(filter(None, supply_quantity_by_fy[fy].values())))
                total_revenue = replace_none_with_zero(sum(filter(None, revenue_by_fy[fy].values())))
                total_expense = replace_none_with_zero(sum(filter(None, expense_by_fy[fy].values())))
                total_contribution = replace_none_with_zero(sum(filter(None, contribution_by_fy[fy].values())))
                total_excess_demand = replace_none_with_zero(total_demand_quantity - total_supply_quantity)

                product_data_by_fy[fy].append({
                    'product': product,
                    'projections': projections_by_fy[fy],
                    'demand_quantity': demand_quantity_by_fy[fy],
                    'total_tanks': tank_quantity_by_fy[fy],
                    'supply_quantity': supply_quantity_by_fy[fy],
                    'price': product_price,
                    'variable_cost': variable_cost,
                    'revenue': revenue_by_fy[fy],
                    'expense': expense_by_fy[fy],
                    'contribution': contribution_by_fy[fy],

                    'total_projection': total_projection,
                    'total_demand_quantity': total_demand_quantity,
                    'total_tank_quantity': total_tank_quantity,
                    'total_supply_quantity': total_supply_quantity,
                    'total_excess_demand': total_excess_demand,
                    'excess_pct': round(total_excess_demand * 100 / total_demand_quantity,
                                        2) if total_demand_quantity != 0 else 0,
                    'total_revenue': total_revenue,
                    'total_expense': total_expense,
                    'total_contribution': total_contribution,
                })

        return product_data_by_fy

    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)
    marketing_costs = MarketingEntry.objects.filter(cycle=current_cycle)
    products_filter = Product.objects.filter(cycle=current_cycle)
    products = products_filter.prefetch_related('targeted_market_size')
    retail_products = products.filter(product_distribution='retail')
    wholesale_products = products.filter(product_distribution='wholesale')

    split_products = [
        (prepare_tms_data(retail_products, current_cycle), 'Retail'),
        (prepare_tms_data(wholesale_products, current_cycle), 'Wholesale'),
    ]

    sales_projections = prepare_sales_projections(products, current_cycle)
    spl_offer = products[:1]

    context = {
        'show_project_navbar': True,
        'current_cycle': current_cycle,
        'underlying_cycle': current_cycle.underlying_cycle,
        'marketing_costs': marketing_costs,
        'products': products,
        'split_products': split_products,
        'fy_list': [
            1, 2, 3
        ],
        'months': [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ],
        'sales_projections': sales_projections,
        'spl_offer': spl_offer,
    }

    return render(
        request,
        'operations_management/operations_management.html',
        context
    )


# Marketing Cost
@login_required
def marketing_management(request):
    def prepare_tms_data(products, cycle):
        product_data = []
        for product in products:
            tms_data = list(
                product.targeted_market_size.filter(cycle=cycle).values('fy', 'tms_pct', 'tms_value', 'cycle'))

            # Initialize default TMS data for new products
            default_tms_data = {'FY1': None, 'FY2': None, 'FY3': None}
            # Populate with actual data if available
            tms_dict = {fy: tms for fy, tms in default_tms_data.items()}
            for tms in tms_data:
                tms_dict[tms['fy']] = tms

            product_info = {
                'product_pk': product.product_pk,
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_distribution': product.product_distribution,
                'cycle': cycle,
                'tms': tms_dict,
            }
            product_data.append(product_info)
        return product_data

    def prepare_sales_projections(product_list, cycle):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        product_data_by_fy = {fy: [] for fy in financial_years}

        for product in product_list:
            projections_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            demand_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            tank_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            supply_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            revenue_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            expense_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            contribution_by_fy = {fy: {month: None for month in months} for fy in financial_years}

            product_price = product.price
            variable_cost = product.material_cost + product.labor_cost + product.other_cost

            for projection in product.sales_projection.filter(cycle=cycle):
                if projection.fy in projections_by_fy:
                    projections_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.projection)
                    demand_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.demand_quantity)
                    tank_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.tank_quantity)
                    supply_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.supply_quantity)
                    revenue_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.revenue)
                    expense_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.expense)
                    contribution_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.contribution)

            for fy in financial_years:
                total_projection = replace_none_with_zero(sum(filter(None, projections_by_fy[fy].values())))
                total_demand_quantity = replace_none_with_zero(sum(filter(None, demand_quantity_by_fy[fy].values())))
                total_tank_quantity = replace_none_with_zero(sum(filter(None, tank_quantity_by_fy[fy].values())))
                total_supply_quantity = replace_none_with_zero(sum(filter(None, supply_quantity_by_fy[fy].values())))
                total_revenue = replace_none_with_zero(sum(filter(None, revenue_by_fy[fy].values())))
                total_expense = replace_none_with_zero(sum(filter(None, expense_by_fy[fy].values())))
                total_contribution = replace_none_with_zero(sum(filter(None, contribution_by_fy[fy].values())))
                total_excess_demand = replace_none_with_zero(total_demand_quantity - total_supply_quantity)

                product_data_by_fy[fy].append({
                    'product': product,
                    'projections': projections_by_fy[fy],
                    'demand_quantity': demand_quantity_by_fy[fy],
                    'total_tanks': tank_quantity_by_fy[fy],
                    'supply_quantity': supply_quantity_by_fy[fy],
                    'price': product_price,
                    'variable_cost': variable_cost,
                    'revenue': revenue_by_fy[fy],
                    'expense': expense_by_fy[fy],
                    'contribution': contribution_by_fy[fy],

                    'total_projection': total_projection,
                    'total_demand_quantity': total_demand_quantity,
                    'total_tank_quantity': total_tank_quantity,
                    'total_supply_quantity': total_supply_quantity,
                    'total_excess_demand': total_excess_demand,
                    'excess_pct': round(total_excess_demand * 100 / total_demand_quantity,
                                        2) if total_demand_quantity != 0 else 0,
                    'total_revenue': total_revenue,
                    'total_expense': total_expense,
                    'total_contribution': total_contribution,
                })

        return product_data_by_fy

    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)
    marketing_costs = MarketingEntry.objects.filter(cycle=current_cycle)
    products_filter = Product.objects.filter(cycle=current_cycle)
    products = products_filter.prefetch_related('targeted_market_size')
    retail_products = products.filter(product_distribution='retail')
    wholesale_products = products.filter(product_distribution='wholesale')

    split_products = [
        (prepare_tms_data(retail_products, current_cycle), 'Retail'),
        (prepare_tms_data(wholesale_products, current_cycle), 'Wholesale'),
    ]

    sales_projections = prepare_sales_projections(products, current_cycle)
    spl_offer = products[:1]

    context = {
        'show_project_navbar': True,
        'current_cycle': current_cycle,
        'underlying_cycle': current_cycle.underlying_cycle,
        'marketing_costs': marketing_costs,
        'products': products,
        'split_products': split_products,
        'fy_list': [
            1, 2, 3
        ],
        'months': [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ],
        'sales_projections': sales_projections,
        'spl_offer': spl_offer,
    }

    return render(
        request,
        'marketing_management/marketing_management.html',
        context
    )


@login_required
def marketing_cost_add(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)
    if request.method == 'POST':
        form = MarketingEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.cycle = current_cycle  # Assigning the current user
            entry.project = current_project
            entry.save()
            return redirect('marketing_management')
    else:
        form = MarketingEntryForm()

    context = {
        'form': form,
        'edit_mode': False,
    }

    return render(
        request,
        'marketing_management/marketing_costs/marketing_cost_form.html',
        context
    )


@login_required
def marketing_cost_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(MarketingEntry, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('marketing_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = MarketingEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('marketing_management')
    else:
        form = MarketingEntryForm(instance=entry)

    context = {
        'form': form,
        'edit_mode': True,
    }

    return render(
        request,
        'marketing_management/marketing_costs/marketing_cost_form.html',
        context
    )


@login_required
def marketing_cost_delete(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(MarketingEntry, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('marketing_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        entry.delete()
        return redirect('marketing_management')

    context = {
        'entry': entry,
    }

    return render(
        request,
        'marketing_management/marketing_costs/marketing_cost_confirm_delete.html',
        context
    )


# Product
@login_required
def product_add(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)

    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.cycle = current_cycle  # Assigning the current user
            entry.project = current_project
            entry.save()

            # Create sales projection records for the new product
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            fys = [1, 2, 3]

            for fy in fys:
                for month in months:
                    SalesProjection.objects.create(
                        product=entry,
                        fy=fy,
                        month=month,
                        cycle=current_cycle,
                        project=current_project,
                        projection=0  # Or any default value you deem appropriate
                    )

            return redirect('marketing_management')
    else:
        form = ProductForm()

    context = {
        'form': form
    }

    return render(
        request,
        'marketing_management/product/product_form.html',
        context
    )


@login_required
def product_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Product, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('marketing_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()

            # Fetch and save related models
            related_sales_projections = SalesProjection.objects.filter(product=entry)
            # related_tms = TargetMarketSize.objects.filter(product=entry)
            #
            # for tms in related_tms:
            #     tms.save()

            for sales_projection in related_sales_projections:
                sales_projection.save()

            return redirect('marketing_management')
    else:
        form = ProductForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'marketing_management/product/product_form.html',
        context
    )


@login_required
def product_delete(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Product, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('marketing_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        entry.delete()
        return redirect('marketing_management')

    context = {
        'form': entry,
    }

    return render(
        request,
        'marketing_management/product/product_confirm_delete.html',
        context
    )


@login_required
def targeted_marketsize_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)

    fy_choices = [1, 2, 3]
    product = Product.objects.get(pk=pk)
    existing_tms = TargetMarketSize.objects.filter(product_id=pk)
    existing_fys = existing_tms.values_list('fy', flat=True)

    # Check for missing FY entries and initialize them
    missing_fys = set(fy_choices) - set(existing_fys)
    for fy in missing_fys:
        TargetMarketSize.objects.create(product_id=pk,
                                        project=current_project,
                                        fy=fy,
                                        cycle=current_cycle,
                                        tms_pct=0)  # Or any default value

    TargetMarketSizeFormSet = modelformset_factory(
        TargetMarketSize,
        form=TargetMarketSizeForm,
        extra=0  # No extra forms, since all FYs should now have an entry
    )

    if request.method == 'POST':
        formset = TargetMarketSizeFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            # Redirect or handle the next steps
            return redirect('marketing_management')
    else:
        formset = TargetMarketSizeFormSet(queryset=TargetMarketSize.objects.filter(product_id=pk))

    context = {
        'formset': formset,
        'product': product,
    }

    return render(
        request,
        'marketing_management/targeted_marketsize/targeted_marketsize_form.html',
        context
    )


@login_required
def sales_projection_edit(request, pk, fy):
    product = Product.objects.get(pk=pk)

    # Filter the queryset for the formset to include only the projections for the selected year
    queryset = SalesProjection.objects.filter(product_id=pk, fy=fy)

    # Define the formset with the filtered queryset
    SalesProjectFormSet = modelformset_factory(SalesProjection, form=SalesProjectionForm, extra=0)
    formset = SalesProjectFormSet(queryset=queryset)

    if request.method == 'POST':
        formset = SalesProjectFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect('marketing_management')  # Ensure you redirect to the desired view

    context = {
        'formset': formset,
        'product': product,
        'selected_year': fy,
    }

    return render(
        request,
        'marketing_management/sales_projections/sales_projection_edit.html',
        context
    )


@login_required
def financial_management(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    # Marketing Costs
    marketing_costs = MarketingEntry.objects.filter(cycle=current_cycle)

    # Employees
    employees = Employee.objects.filter(cycle=current_cycle)

    # Utilities, Supplies and other
    utilities = Utility.objects.filter(cycle=current_cycle)

    # Rent
    rents = Rent.objects.filter(cycle=current_cycle)

    # Debt
    debts = Debt.objects.filter(cycle=current_cycle)

    # Tax
    taxes = Tax.objects.filter(cycle=current_cycle)

    # Financial Market Indicators
    financial_market_indicators = FinancialMarketIndicator.objects.filter(cycle=current_cycle)

    context = {
        'current_cycle': current_cycle,
        'underlying_cycle': current_cycle.underlying_cycle,
        'show_project_navbar': True,
        'employees': employees,
        'utilities': utilities,
        'marketing_costs': marketing_costs,
        'rentals': rents,
        'taxes': taxes,
        'debts': debts,
        'financial_market_indicators': financial_market_indicators,
    }

    return render(
        request,
        'financial_management/financial_management.html',
        context
    )


@login_required
def organization_management(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    # Employees
    employees = Employee.objects.filter(cycle=current_cycle)

    context = {
        'current_cycle': current_cycle,
        'underlying_cycle': current_cycle.underlying_cycle,
        'show_project_navbar': True,
        'employees': employees,
    }

    return render(
        request,
        'organization_management/organization_management.html',
        context
    )


@login_required
def employee_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Employee, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = EmployeeForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'financial_management/employees/employee_edit.html',
        context
    )


@login_required
def utility_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Utility, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = UtilityForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = UtilityForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'financial_management/utilities/utility_edit.html',
        context
    )


@login_required
def rent_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Rent, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = RentForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = RentForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'financial_management/rents/rent_edit.html',
        context
    )


@login_required
def tax_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Tax, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = TaxForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = TaxForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'financial_management/taxes/tax_edit.html',
        context
    )


@login_required
def fmi_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(FinancialMarketIndicator, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = FMIForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = FMIForm(instance=entry)

    context = {
        'form': form,
    }

    return render(
        request,
        'financial_management/financial_market_indicators/fmi_edit.html',
        context
    )


# Debt
@login_required
def debt_add(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)

    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.cycle = current_cycle  # Assigning the current user
            entry.project = current_project
            entry.save()
            return redirect('financial_management')
    else:
        form = DebtForm()

    context = {
        'form': form,
        'edit_mode': False,
    }

    return render(
        request,
        'financial_management/debts/debt_add.html',
        context
    )


@login_required
def debt_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Debt, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = DebtForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('financial_management')
    else:
        form = DebtForm(instance=entry)

    context = {
        'form': form,
        'edit_mode': True,
    }

    return render(
        request,
        'financial_management/debts/debt_add.html',
        context
    )


@login_required
def debt_delete(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Debt, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('financial_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        entry.delete()
        return redirect('financial_management')

    context = {
        'entry': entry,
    }

    return render(
        request,
        'financial_management/debts/debt_delete.html',
        context
    )


def sum_decimals(*args):
    total = float(0)
    for number in args:
        if number is not None:
            total += float(number)
    return total


def convert_to_float(arg):
    return float(arg) if arg is not None else 0


def compare_cycles(request):
    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id) if current_project_id else None

    form = CycleComparisonForm(request.POST or None, project=current_project)
    if request.method == 'POST' and form.is_valid():
        selected_cycles = form.cleaned_data['cycles']
        cycle_ids = [cycle.id for cycle in selected_cycles]
        request.session['selected_cycle_ids'] = cycle_ids
        return redirect('sim_report')

    context = {
        'form': form
    }

    return render(
        request,
        'pro_forma/compare_cycles.html',
        context
    )


def plot_breakeven_point(break_even_months, break_even_sales, total_fixed_cost):
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the three lines
    # Line from (0, 0) to (break_even_months, break_even_sales)
    ax.plot([0, break_even_months], [0, break_even_sales], label='Total Revenue', marker='o', color='black')

    # Line from (0, total_fixed_cost) to (break_even_months, break_even_sales)
    ax.plot([0, break_even_months], [total_fixed_cost, break_even_sales], label='Total Cost', marker='o',
            color='blue')

    # Line from (0, total_fixed_cost) to (break_even_months, total_fixed_cost)
    ax.plot([0, break_even_months], [total_fixed_cost, total_fixed_cost], label='Fixed Cost', linestyle='--',
            marker='o', color='red')

    # Set labels and title
    ax.set_xlabel('Months')
    ax.set_ylabel('Total Revenue ($)')
    ax.set_title('Break-even Point Analysis')

    # Increase x and y axis range by 20%
    ax.set_xlim(0, break_even_months * 1.2)
    ax.set_ylim(0, break_even_sales * 2)

    # Add legend
    ax.legend()

    # Show grid
    ax.grid(True)

    # Save plot to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_breakeven = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.clf()
    return plot_breakeven


def plot_efficiency_ratios(direction, *args):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Define fiscal years
    fiscal_years = ["FY1", "FY2", "FY3"]

    # Plot the efficiency ratios with increased line thickness
    for label, data in args:
        print(label, data)
        ax.plot(fiscal_years, list(data.values()), label=label, marker='o', linewidth=2)

    xlim = ax.get_xlim()
    ylim = (0, 0.8)
    ax.set_ylim(ylim)  # Set y-axis limit from 0 to 1

    start_pos, end_pos = ((xlim[0] + 0.2 * (xlim[1] - xlim[0]), ylim[1] - 0.2 * (ylim[1] - ylim[0])),
                          (xlim[1] - 0.2 * (xlim[1] - xlim[0]),
                           ylim[0] + 0.2 * (ylim[1] - ylim[0]))) if direction == "down" else \
        ((xlim[0] + 0.2 * (xlim[1] - xlim[0]), ylim[0] + 0.2 * (ylim[1] - ylim[0])),
         (xlim[1] - 0.2 * (xlim[1] - xlim[0]), ylim[1] - 0.2 * (ylim[1] - ylim[0])))

    # Create and add the arrow line
    arrow = FancyArrow(start_pos[0], start_pos[1], end_pos[0] - start_pos[0], end_pos[1] - start_pos[1],
                       width=0.02, head_width=0.1, head_length=0.1, color='red', alpha=0.5)
    ax.add_patch(arrow)

    # Create a dummy line for the arrow legend
    arrow_legend = mlines.Line2D([], [], color='red', linestyle='-', linewidth=2, label='Recommended Direction')

    # Add all lines and the arrow to the legend
    handles, labels = ax.get_legend_handles_labels()
    handles.append(arrow_legend)
    labels.append('Recommended Direction')
    ax.legend(handles=handles, labels=labels)

    # Set labels and title
    ax.set_xlabel('Fiscal Year')
    ax.set_ylabel('Efficiency Ratio')
    ax.set_title('Efficiency Ratios Over Fiscal Years')

    # Save plot to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)

    plot_efficiency = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.clf()

    return plot_efficiency


# def print_request(request):
#     print("Method:", request.method, "\n")
#     print("Full URL:", request.build_absolute_uri(), "\n")
#     print("Headers:", request.headers, "\n")
#     print("GET parameters:", request.GET, "\n")
#     print("POST data:", request.POST, "\n")
#     print("Raw body:", request.body, "\n")
#     print("Path:", request.path, "\n")
#     print("User Agent:", request.META.get('HTTP_USER_AGENT'), "\n")
#     print("Client IP:", request.META.get('REMOTE_ADDR'), "\n")
#
#     print("Session variables:")
#     for key, value in request.session.items():
#         print(f"Session key: {key} | Session value: {value}")


def sim_report(request):
    def prepare_sales_projections(product_list, cycle):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        product_data_by_fy = {fy: [] for fy in financial_years}
        total_revenue_by_fy = {fy: 0 for fy in financial_years}
        total_expense_by_fy = {fy: 0 for fy in financial_years}
        total_contribution_by_fy = {fy: 0 for fy in financial_years}

        for product in product_list:
            projections_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            demand_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            tank_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            supply_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            revenue_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            expense_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            contribution_by_fy = {fy: {month: None for month in months} for fy in financial_years}

            product_price = product.price
            variable_cost = product.material_cost + product.labor_cost + product.other_cost

            for projection in product.sales_projection.filter(cycle=cycle):
                if projection.fy in projections_by_fy:
                    projections_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.projection)
                    demand_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.demand_quantity)
                    tank_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.tank_quantity)
                    supply_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.supply_quantity)
                    revenue_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.revenue)
                    expense_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.expense)
                    contribution_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.contribution)

            for fy in financial_years:
                total_projection = replace_none_with_zero(sum(filter(None, projections_by_fy[fy].values())))
                total_demand_quantity = replace_none_with_zero(sum(filter(None, demand_quantity_by_fy[fy].values())))
                total_tank_quantity = replace_none_with_zero(sum(filter(None, tank_quantity_by_fy[fy].values())))
                total_supply_quantity = replace_none_with_zero(sum(filter(None, supply_quantity_by_fy[fy].values())))
                total_revenue = replace_none_with_zero(sum(filter(None, revenue_by_fy[fy].values())))
                total_expense = replace_none_with_zero(sum(filter(None, expense_by_fy[fy].values())))
                total_contribution = replace_none_with_zero(sum(filter(None, contribution_by_fy[fy].values())))
                total_excess_demand = replace_none_with_zero(total_demand_quantity - total_supply_quantity)

                # Update the total aggregates for each financial year
                total_revenue_by_fy[fy] += replace_none_with_zero(total_revenue)
                total_expense_by_fy[fy] += replace_none_with_zero(total_expense)
                total_contribution_by_fy[fy] += replace_none_with_zero(total_contribution)

                product_data_by_fy[fy].append({
                    'product': product,
                    'projections': projections_by_fy[fy],
                    'demand_quantity': demand_quantity_by_fy[fy],
                    'total_tanks': tank_quantity_by_fy[fy],
                    'supply_quantity': supply_quantity_by_fy[fy],
                    'price': product_price,
                    'variable_cost': variable_cost,
                    'revenue': revenue_by_fy[fy],
                    'expense': expense_by_fy[fy],
                    'contribution': contribution_by_fy[fy],

                    'total_projection': total_projection,
                    'total_demand_quantity': total_demand_quantity,
                    'total_tank_quantity': total_tank_quantity,
                    'total_supply_quantity': total_supply_quantity,
                    'total_excess_demand': total_excess_demand,
                    'excess_pct': round(total_excess_demand * 100 / total_demand_quantity,
                                        2) if total_demand_quantity != 0 else 0,
                    'total_revenue': total_revenue,
                    'total_expense': total_expense,
                    'total_contribution': total_contribution,
                })

        return product_data_by_fy, total_revenue_by_fy, total_expense_by_fy, total_contribution_by_fy

    def prepare_fixed_costs(cycle_id):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        fixed_costs_by_fy = {fy: {month: {} for month in months} for fy in financial_years}
        total_fixed_cost_by_fy = {fy: 0 for fy in financial_years}

        # Aggregating marketing payments and replacing None with 0
        marketing_payments = [
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy1_value'))['total']),
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy2_value'))['total']),
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy3_value'))['total'])
        ]

        # Aggregating employee budgets and replacing None with 0
        employees_budget = [
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy1'))['total']),
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy2'))['total']),
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy3'))['total'])
        ]

        # Aggregating utility budgets and replacing None with 0
        utilities_budget = [
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy1'))['total']),
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy2'))['total']),
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy3'))['total'])
        ]

        # Aggregating rent payments and replacing None with 0
        rent_payments = [
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy1'))['total']),
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy2'))['total']),
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy3'))['total'])
        ]

        debt_payments = [
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy1'))['total']),
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy2'))['total']),
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy3'))['total'])
        ]

        # Calculating total fixed costs and replacing None with 0
        total_fixed_costs = [
            sum_decimals(marketing_payments[0], employees_budget[0], utilities_budget[0], rent_payments[0],
                         debt_payments[0]),
            sum_decimals(marketing_payments[1], employees_budget[1], utilities_budget[1], rent_payments[1],
                         debt_payments[1]),
            sum_decimals(marketing_payments[2], employees_budget[2], utilities_budget[2], rent_payments[2],
                         debt_payments[2]),
        ]

        for fy, (marketing, employee, utility, rent, debt, total_cost) in enumerate(
                zip(marketing_payments, employees_budget, utilities_budget, rent_payments, debt_payments,
                    total_fixed_costs), start=1):
            for month in months:
                fixed_costs_by_fy[fy][month] = {
                    'Employee Salaries': round(employee / 12, 2) if employee is not None else 0,
                    'Utilities & Other': round(utility / 12, 2) if utility is not None else 0,
                    'Marketing Costs': round(marketing / 12, 2) if marketing is not None else 0,
                    'Rent': round(rent / 12, 2) if rent is not None else 0,
                    'Debt': round(debt / 12, 2) if debt is not None else 0,
                    'Total Fixed Costs': round(total_cost / 12, 2) if total_cost is not None else 0,
                }
            total_fixed_cost_by_fy[fy] = convert_to_float(total_cost)

        fixed_costs = {
            'Employee Salaries': employees_budget,
            'Utilities & Other': utilities_budget,
            'Marketing Costs': marketing_payments,
            'Rent': rent_payments,
            'Debt': debt_payments,
            'Total Fixed Costs': total_fixed_costs,
        }

        return fixed_costs_by_fy, fixed_costs, total_fixed_cost_by_fy

    cycle_ids = request.session.get('selected_cycle_ids', [])
    if not cycle_ids:
        return redirect('compare_cycles')  # Redirect if no cycles selected

    selected_cycles = Cycle.objects.filter(id__in=cycle_ids)

    comparison_data = []
    for cycle in selected_cycles:
        products_filter = Product.objects.filter(cycle=cycle)
        products = products_filter.prefetch_related('targeted_market_size')
        product_data_by_fy, total_revenue_by_fy, total_expense_by_fy, total_contribution_by_fy = prepare_sales_projections(
            products, cycle)
        all_fixed_costs = prepare_fixed_costs(cycle.id)

        tax_record = Tax.objects.filter(cycle=cycle).first()
        tax_rate = (25 / 100)
        if tax_record:
            tax_rate = tax_record.tax_pct

        total_fixed_cost_by_fy = all_fixed_costs[2]

        total_gross_profit = {
            fy: convert_to_float(total_contribution_by_fy[fy]) - convert_to_float(total_fixed_cost_by_fy[fy])
            for fy in [1, 2, 3]
        }

        total_net_profit = {
            fy: convert_to_float(total_gross_profit[fy]) - (
                    convert_to_float(total_gross_profit[fy]) * convert_to_float(tax_rate) / 100)
            for fy in [1, 2, 3]
        }

        total_revenue = sum(total_revenue_by_fy.values())
        total_contribution = sum(total_contribution_by_fy.values())

        marketing_costs_by_fy = {
            fy: replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle).aggregate(total=Sum(f'payment_fy{fy}_value'))['total'])
            for fy in [1, 2, 3]
        }

        management_compensation_by_fy = {
            fy: replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle).aggregate(total=Sum(f'employee_budget_fy{fy}'))['total'])
            for fy in [1, 2, 3]
        }

        fctr_by_fy = {
            fy: round(
                replace_none_with_zero(safe_division(convert_to_float(total_fixed_cost_by_fy[fy]),
                                                     convert_to_float(total_revenue_by_fy[fy]))), 2)
            for fy in [1, 2, 3]
        }

        mctr_by_fy = {
            fy: round(
                replace_none_with_zero(safe_division(convert_to_float(management_compensation_by_fy[fy]),
                                                     convert_to_float(total_revenue_by_fy[fy]))), 2)
            for fy in [1, 2, 3]
        }

        actr_by_fy = {
            fy: round(
                replace_none_with_zero(safe_division(convert_to_float(marketing_costs_by_fy[fy]),
                                                     convert_to_float(total_revenue_by_fy[fy]))), 2)
            for fy in [1, 2, 3]
        }

        gptr_by_fy = {
            fy: round(
                replace_none_with_zero(
                    safe_division(convert_to_float(total_gross_profit[fy]), convert_to_float(total_revenue_by_fy[fy]))),
                2)
            for fy in [1, 2, 3]
        }

        nptr_by_fy = {
            fy: round(
                replace_none_with_zero(
                    safe_division(convert_to_float(total_net_profit[fy]), convert_to_float(total_revenue_by_fy[fy]))),
                2)
            for fy in [1, 2, 3]
        }

        total_nptr = replace_none_with_zero(
            safe_division(convert_to_float(sum(total_net_profit.values())), convert_to_float(total_revenue)))
        total_gptr = replace_none_with_zero(
            safe_division(convert_to_float(sum(total_gross_profit.values())), convert_to_float(total_revenue)))

        contribution_margin = round(replace_none_with_zero(safe_division(total_contribution, total_revenue)) * 100, 2)

        break_even_months = round(replace_none_with_zero(
            safe_division(convert_to_float(sum(total_fixed_cost_by_fy.values())) * 12,
                          convert_to_float(total_contribution))), 2)

        break_even_sales = round(replace_none_with_zero(
            safe_division(convert_to_float(sum(total_fixed_cost_by_fy.values())) * 12,
                          convert_to_float(contribution_margin))), 2)


        # bep_plot_by_fy = {
        #     fy: plot_breakeven_point(break_even_months, break_even_sales, total_fixed_cost_by_fy[1])
        #     for fy in [1, 2, 3]
        # }

        break_even_plot = plot_breakeven_point(break_even_months, break_even_sales, total_fixed_cost_by_fy[1])

        bep_plot_by_fy = {
            fy: break_even_plot

            for fy in [1, 2, 3]
        }

        cost_list = [
            ("Fixed Cost: Total revenue", fctr_by_fy),
            ("Management Cost: Total revenue", mctr_by_fy),
            ("Advertising Cost: Total revenue", actr_by_fy),
        ]

        profit_list = [
            ("Gross Profit: Total revenue", gptr_by_fy),
            ("Net Profit: Total revenue", nptr_by_fy),
        ]

        # Call the function with unpacked lists
        cost_plot = plot_efficiency_ratios("down", *cost_list)
        profit_plot = plot_efficiency_ratios("up", *profit_list)

        metrics = {
            'cycle': cycle,
            'total_revenue': total_revenue,
            'total_revenue_fy1': total_revenue_by_fy[1],
            'total_revenue_fy2': total_revenue_by_fy[2],
            'total_revenue_fy3': total_revenue_by_fy[3],

            'total_gross_profit': sum(total_gross_profit.values()),
            'total_gross_profit_fy1': total_gross_profit[1],
            'total_gross_profit_fy2': total_gross_profit[2],
            'total_gross_profit_fy3': total_gross_profit[3],

            'total_net_profit': sum(total_net_profit.values()),
            'total_net_profit_fy1': total_net_profit[1],
            'total_net_profit_fy2': total_net_profit[2],
            'total_net_profit_fy3': total_net_profit[3],

            'total_fctr_fy1': fctr_by_fy[1],
            'total_fctr_fy2': fctr_by_fy[2],
            'total_fctr_fy3': fctr_by_fy[3],

            'total_mctr_fy1': mctr_by_fy[1],
            'total_mctr_fy2': mctr_by_fy[2],
            'total_mctr_fy3': mctr_by_fy[3],

            'total_actr_fy1': actr_by_fy[1],
            'total_actr_fy2': actr_by_fy[2],
            'total_actr_fy3': actr_by_fy[3],

            'total_gptr': total_gptr,
            'total_gptr_fy1': gptr_by_fy[1],
            'total_gptr_fy2': gptr_by_fy[2],
            'total_gptr_fy3': gptr_by_fy[3],

            'total_nptr': total_nptr,
            'total_nptr_fy1': nptr_by_fy[1],
            'total_nptr_fy2': nptr_by_fy[2],
            'total_nptr_fy3': nptr_by_fy[3],

            'break_even_months_fy1': break_even_months,
            # 'break_even_months_fy2': bep_months_by_fy[2],
            # 'break_even_months_fy3': bep_months_by_fy[3],

            'break_even_sales_fy1': break_even_sales,
            # 'break_even_sales_fy2': bep_sales_by_fy[2],
            # 'break_even_sales_fy3': bep_sales_by_fy[3],

            'break_even_plot': break_even_plot,
            # 'break_even_plot_fy2': bep_plot_by_fy[2],
            # 'break_even_plot_fy3': bep_plot_by_fy[3],

            'cost_plot': cost_plot,
            'profit_plot': profit_plot,
        }

        comparison_data.append(metrics)

    context = {
        'comparison_data': comparison_data,
        'heading_colspan': len(comparison_data) + 1,
        'show_project_navbar': True,
    }

    return render(
        request,
        'pro_forma/sim_report.html',
        context
    )


def pro_forma(request):
    def prepare_sales_projections(product_list, cycle):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        product_data_by_fy = {fy: [] for fy in financial_years}
        total_sales_by_fy = {fy: 0 for fy in financial_years}
        total_revenue_by_fy = {fy: 0 for fy in financial_years}
        total_expense_by_fy = {fy: 0 for fy in financial_years}
        total_contribution_by_fy = {fy: 0 for fy in financial_years}

        for product in product_list:
            projections_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            demand_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            tank_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            supply_quantity_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            revenue_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            expense_by_fy = {fy: {month: None for month in months} for fy in financial_years}
            contribution_by_fy = {fy: {month: None for month in months} for fy in financial_years}

            product_price = product.price
            variable_cost = product.material_cost + product.labor_cost + product.other_cost

            for projection in product.sales_projection.filter(cycle=cycle):
                if projection.fy in projections_by_fy:
                    projections_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.projection)
                    demand_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.demand_quantity)
                    tank_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.tank_quantity)
                    supply_quantity_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.supply_quantity)
                    revenue_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.revenue)
                    expense_by_fy[projection.fy][projection.month] = replace_none_with_zero(projection.expense)
                    contribution_by_fy[projection.fy][projection.month] = replace_none_with_zero(
                        projection.contribution)

            for fy in financial_years:
                total_projection = replace_none_with_zero(sum(filter(None, projections_by_fy[fy].values())))
                total_demand_quantity = replace_none_with_zero(sum(filter(None, demand_quantity_by_fy[fy].values())))
                total_tank_quantity = replace_none_with_zero(sum(filter(None, tank_quantity_by_fy[fy].values())))
                total_supply_quantity = replace_none_with_zero(sum(filter(None, supply_quantity_by_fy[fy].values())))
                total_revenue = replace_none_with_zero(sum(filter(None, revenue_by_fy[fy].values())))
                total_expense = replace_none_with_zero(sum(filter(None, expense_by_fy[fy].values())))
                total_contribution = replace_none_with_zero(sum(filter(None, contribution_by_fy[fy].values())))
                total_excess_demand = replace_none_with_zero(total_demand_quantity - total_supply_quantity)

                # Update the total aggregates for each financial year
                total_sales_by_fy[fy] += replace_none_with_zero(total_supply_quantity)
                total_revenue_by_fy[fy] += replace_none_with_zero(total_revenue)
                total_expense_by_fy[fy] += replace_none_with_zero(total_expense)
                total_contribution_by_fy[fy] += replace_none_with_zero(total_contribution)

                product_data_by_fy[fy].append({
                    'product': product,
                    'projections': projections_by_fy[fy],
                    'demand_quantity': demand_quantity_by_fy[fy],
                    'total_tanks': tank_quantity_by_fy[fy],
                    'supply_quantity': supply_quantity_by_fy[fy],
                    'price': product_price,
                    'variable_cost': variable_cost,
                    'revenue': revenue_by_fy[fy],
                    'expense': expense_by_fy[fy],
                    'contribution': contribution_by_fy[fy],

                    'total_projection': total_projection,
                    'total_demand_quantity': total_demand_quantity,
                    'total_tank_quantity': total_tank_quantity,
                    'total_supply_quantity': total_supply_quantity,
                    'total_excess_demand': total_excess_demand,
                    'excess_pct': round(total_excess_demand * 100 / total_demand_quantity,
                                        2) if total_demand_quantity != 0 else 0,
                    'total_revenue': total_revenue,
                    'total_expense': total_expense,
                    'total_contribution': total_contribution,
                })

        return product_data_by_fy, total_sales_by_fy, total_revenue_by_fy, total_expense_by_fy, total_contribution_by_fy

    def prepare_fixed_costs(cycle_id):
        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        fixed_costs_by_fy = {fy: {month: {} for month in months} for fy in financial_years}
        total_fixed_cost_by_fy = {fy: 0 for fy in financial_years}

        # Aggregating marketing payments and replacing None with 0
        marketing_payments = [
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy1_value'))['total']),
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy2_value'))['total']),
            replace_none_with_zero(
                MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy3_value'))['total'])
        ]

        # Aggregating employee budgets and replacing None with 0
        employees_budget = [
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy1'))['total']),
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy2'))['total']),
            replace_none_with_zero(
                Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy3'))['total'])
        ]

        # Aggregating utility budgets and replacing None with 0
        utilities_budget = [
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy1'))['total']),
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy2'))['total']),
            replace_none_with_zero(
                Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy3'))['total'])
        ]

        # Aggregating rent payments and replacing None with 0
        rent_payments = [
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy1'))['total']),
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy2'))['total']),
            replace_none_with_zero(
                Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy3'))['total'])
        ]

        debt_payments = [
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy1'))['total']),
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy2'))['total']),
            replace_none_with_zero(
                Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy3'))['total'])
        ]

        # Calculating total fixed costs and replacing None with 0
        total_fixed_costs = [
            sum_decimals(marketing_payments[0], employees_budget[0], utilities_budget[0], rent_payments[0],
                         debt_payments[0]),
            sum_decimals(marketing_payments[1], employees_budget[1], utilities_budget[1], rent_payments[1],
                         debt_payments[1]),
            sum_decimals(marketing_payments[2], employees_budget[2], utilities_budget[2], rent_payments[2],
                         debt_payments[2]),
        ]

        for fy, (marketing, employee, utility, rent, debt, total_cost) in enumerate(
                zip(marketing_payments, employees_budget, utilities_budget, rent_payments, debt_payments,
                    total_fixed_costs), start=1):
            for month in months:
                fixed_costs_by_fy[fy][month] = {
                    'Employee Salaries': round(employee / 12, 2) if employee is not None else 0,
                    'Utilities & Other': round(utility / 12, 2) if utility is not None else 0,
                    'Marketing Costs': round(marketing / 12, 2) if marketing is not None else 0,
                    'Rent': round(rent / 12, 2) if rent is not None else 0,
                    'Debt': round(debt / 12, 2) if debt is not None else 0,
                    'Total Fixed Costs': round(total_cost / 12, 2) if total_cost is not None else 0,
                }
            total_fixed_cost_by_fy[fy] = convert_to_float(total_cost)

        fixed_costs = {
            'Employee Salaries': employees_budget,
            'Utilities & Other': utilities_budget,
            'Marketing Costs': marketing_payments,
            'Rent': rent_payments,
            'Debt': debt_payments,
            'Total Fixed Costs': total_fixed_costs,
        }

        return fixed_costs_by_fy, fixed_costs, total_fixed_cost_by_fy

    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)
    marketing_costs = MarketingEntry.objects.filter(cycle=current_cycle)
    products_filter = Product.objects.filter(cycle=current_cycle)
    products = products_filter.prefetch_related('targeted_market_size')

    all_sales_projections, total_sales_by_fy, total_revenue_by_fy, total_expense_by_fy, total_contribution_by_fy = prepare_sales_projections(
        products, current_cycle)

    all_fixed_costs = prepare_fixed_costs(current_cycle_id)

    tax_record = Tax.objects.filter(cycle=current_cycle).first()
    tax_rate = (25 / 100)
    if tax_record:
        tax_rate = tax_record.tax_pct

    total_fixed_cost_by_fy = all_fixed_costs[2]
    total_gross_profit = {
        fy: convert_to_float(total_contribution_by_fy[fy]) - convert_to_float(total_fixed_cost_by_fy[fy])
        for fy in [1, 2, 3]}
    total_net_profit = {fy: convert_to_float(total_gross_profit[fy]) - (
            convert_to_float(total_gross_profit[fy]) * convert_to_float(tax_rate) / 100) for fy in [1, 2, 3]}

    fixed_cost_names = [
        'Employee Salaries',
        'Utilities & Other',
        'Marketing Costs',
        'Rent',
        'Total Fixed Costs',
    ]

    context = {
        'marketing_costs': marketing_costs,
        'products': products,
        'fy_list': [
            1, 2, 3
        ],
        'fy_index': [
            0, 1, 2
        ],
        'months': [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
        ],
        'sales_projections': all_sales_projections,
        'fixed_cost_names': fixed_cost_names,
        'annual_fixed_costs': all_fixed_costs[0],
        'annual_totals_fixed_costs': all_fixed_costs[1],
        'show_project_navbar': True,
        'total_revenue_by_fy': total_revenue_by_fy,
        'total_expense_by_fy': total_expense_by_fy,
        'total_contribution_by_fy': total_contribution_by_fy,
        'total_fixed_cost_by_fy': total_fixed_cost_by_fy,
        'total_gross_profit': total_gross_profit,
        'total_net_profit': total_net_profit,
        'total_sales_by_fy': total_sales_by_fy,

        'overall_quantity': sum(filter(None, total_sales_by_fy.values())),
        'overall_revenue': sum(filter(None, total_revenue_by_fy.values())),
        'overall_expense': sum(filter(None, total_expense_by_fy.values())),
        'overall_contribution': sum(filter(None, total_contribution_by_fy.values())),
        'overall_fixed_cost': sum(filter(None, total_fixed_cost_by_fy.values())),
        'overall_gross_profit': sum(filter(None, total_gross_profit.values())),
        'overall_net_profit': sum(filter(None, total_net_profit.values())),
    }

    return render(
        request,
        'pro_forma/pro_forma.html',
        context
    )


@require_POST
@csrf_protect
def set_financial_year(request):
    financial_year = request.POST.get('financial_year')

    if financial_year:
        request.session['marketing-selected-financial-year'] = financial_year

        json_context = {
            'status': 'success',
            'message': 'Financial year set successfully.',
        }

        return JsonResponse(json_context)
    else:
        json_context = {
            'status': 'error',
            'message': 'Financial year not provided.',
        }

        return JsonResponse(json_context)


@user_passes_test(is_admin)
def delete_cycle_view(request):
    if request.method == 'POST':
        form = CycleDeleteForm(request.POST)
        if form.is_valid():
            cycle_id = form.cleaned_data['cycle_id']
            cycle = get_object_or_404(Cycle, id=cycle_id)
            cycle.delete()
            return redirect('delete_cycle_view')  # Redirect to the cycle dashboard or another appropriate page
    else:
        form = CycleDeleteForm()

    context = {
        'form': form,
    }

    return render(request, 'admin_utils/delete_cycle.html', context)


def prepare_fixed_costs(cycle_id):
    financial_years = [1, 2, 3]

    # Aggregating marketing payments and replacing None with 0
    marketing_payments = [
        replace_none_with_zero(
            MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy1_value'))[
                'total']),
        replace_none_with_zero(
            MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy2_value'))[
                'total']),
        replace_none_with_zero(
            MarketingEntry.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('payment_fy3_value'))['total'])
    ]

    # Aggregating employee budgets and replacing None with 0
    employees_budget = [
        replace_none_with_zero(
            Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy1'))['total']),
        replace_none_with_zero(
            Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy2'))['total']),
        replace_none_with_zero(
            Employee.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('employee_budget_fy3'))['total'])
    ]

    # Aggregating utility budgets and replacing None with 0
    utilities_budget = [
        replace_none_with_zero(
            Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy1'))['total']),
        replace_none_with_zero(
            Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy2'))['total']),
        replace_none_with_zero(
            Utility.objects.filter(cycle_id=cycle_id).aggregate(total=Sum('utility_budget_fy3'))['total'])
    ]

    # Aggregating rent payments and replacing None with 0
    rent_payments = [
        replace_none_with_zero(
            Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy1'))['total']),
        replace_none_with_zero(
            Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy2'))['total']),
        replace_none_with_zero(
            Rent.objects.filter(cycle=cycle_id).aggregate(total=Sum('rent_payment_fy3'))['total'])
    ]

    debt_payments = [
        replace_none_with_zero(
            Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy1'))['total']),
        replace_none_with_zero(
            Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy2'))['total']),
        replace_none_with_zero(
            Debt.objects.filter(cycle=cycle_id).aggregate(total=Sum('debt_payment_fy3'))['total'])
    ]

    fixed_costs = {
        'Employee Salaries': employees_budget,
        'Utilities & Other': utilities_budget,
        'Marketing Costs': marketing_payments,
        'Rent': rent_payments,
        'Debt': debt_payments,
    }

    return fixed_costs


def generate_plots(request):
    def dataframe_for_danalysis(request):
        np.random.seed(88)

        def rtri(mi, ml, ma, n):
            s = ma - mi
            c = (ml - mi) / s
            return ss.triang.rvs(c=c, loc=mi, scale=s, size=n)

        def runif(lb, rb, size):
            return ss.uniform.rvs(lb, rb - lb, size)

        financial_years = [1, 2, 3]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        current_cycle_id = request.session['current_cycle_id']
        current_cycle = Cycle.objects.get(id=current_cycle_id)
        products = Product.objects.filter(cycle=current_cycle).select_related('cycle').prefetch_related(
            'sales_projection', 'target_market_sizes')

        tax_record = Tax.objects.filter(cycle=current_cycle).first()
        tax_rate = 0.25  # Default tax rate if not found
        if tax_record:
            tax_rate = replace_none_with_zero(convert_to_float(tax_record.tax_pct) / 100)

        data = pd.DataFrame()
        num_iterations = 10000

        # Prepare product data in a single pass
        product_data = []
        for product in products:
            price = replace_none_with_zero(convert_to_float(product.price))
            variable_cost = replace_none_with_zero(
                convert_to_float(product.material_cost) + convert_to_float(product.labor_cost) + convert_to_float(
                    product.other_cost))

            total_quantity = sum(
                replace_none_with_zero(convert_to_float(projection.tank_quantity) * 1240)
                for projection in product.sales_projection.all()
            )

            product_data.append({
                'product_id': product.product_id,
                'price': price,
                'variable_cost': variable_cost,
                'quantity': total_quantity
            })

        # Populate the dataframe with product data
        for product in product_data:
            product_id = product['product_id']
            price = product['price']
            variable_cost = product['variable_cost']
            quantity = product['quantity']

            data[f"BR-{product_id} Price"] = runif(price - 0.5, price + 0.5, num_iterations).round(2)
            data[f"BR-{product_id} Variable cost"] = rtri(variable_cost - 0.22, variable_cost, variable_cost + 0.28,
                                                          num_iterations).round(2)
            data[f"BR-{product_id} Quantity"] = ss.norm.rvs(quantity, 0.0333 * quantity, num_iterations).round()

            contribution = round(data[f"BR-{product_id} Quantity"] * (
                    data[f"BR-{product_id} Price"] - data[f"BR-{product_id} Variable cost"]), 2)
            data[f"BR-{product_id} Contribution"] = contribution

        # Fetch fixed costs in a single pass
        fixed_costs = prepare_fixed_costs(cycle_id=current_cycle_id)
        for fy in financial_years:
            fy_index = fy - 1

            employee_salary = convert_to_float(fixed_costs['Employee Salaries'][fy_index])
            data[f"Employee Salaries FY {fy}"] = runif(employee_salary - ((5 / 100) * employee_salary),
                                                       employee_salary + ((5 / 100) * employee_salary),
                                                       num_iterations).round(2)

            rent = convert_to_float(fixed_costs['Rent'][fy_index])
            data[f"Rent FY {fy}"] = rent

            debt = convert_to_float(fixed_costs['Debt'][fy_index])
            data[f"Debt FY {fy}"] = debt

            marketing_cost = convert_to_float(fixed_costs['Marketing Costs'][fy_index])
            data[f"Marketing costs FY {fy}"] = runif(marketing_cost - ((5 / 100) * marketing_cost),
                                                     marketing_cost + ((5 / 100) * marketing_cost),
                                                     num_iterations).round(2)

            data[f"Utilities FY {fy}"] = data[f"Employee Salaries FY {fy}"] / 2

        # Calculate totals and profits
        contribution_columns = [col for col in data.columns if 'Contribution' in col]
        data['Total Contribution'] = round(data[contribution_columns].sum(axis=1), 2)

        fixed_cost_columns = [col for col in data.columns if "FY" in col]
        data["Fixed Cost"] = round(data[fixed_cost_columns].sum(axis=1), 2)

        data["Gross Profit"] = round(data["Total Contribution"] - data["Fixed Cost"], 2)
        data["Net Profit"] = round(data["Gross Profit"] - (data["Gross Profit"] * tax_rate), 2)

        return data

    def generate_histogram(df):
        FIGURE_SIZE = (10, 6)
        five_num_summary = df['Net Profit'].describe(percentiles=[.25, .5, .75])[['min', '25%', '50%', '75%', 'max']]
        five_num_summary['Total Data Points'] = len(df)
        plt.figure(figsize=FIGURE_SIZE)
        sns.histplot(df['Net Profit'])
        plt.axvline(five_num_summary['25%'], color='r', linewidth=2, linestyle='--', label='25th Percentile')
        plt.axvline(five_num_summary['75%'], color='g', linewidth=2, linestyle='--', label='75th Percentile')
        plt.legend()
        plt.title('Histogram for Net Profit')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_histogram = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.clf()
        return plot_histogram, five_num_summary

    def generate_density_plot(df):
        FIGURE_SIZE = (10, 6)
        cdf = df[['Total Contribution', 'Fixed Cost', 'Gross Profit', 'Net Profit']]
        cdf_melted = cdf.melt(var_name='Category', value_name='Value')
        plt.figure(figsize=FIGURE_SIZE)
        sns.kdeplot(data=cdf_melted, x='Value', hue='Category', fill=True)
        plt.title('Distribution Overlay Charts for Fixed Costs, Gross Profit, Contributions, and Net Profit')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_density = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.clf()
        return plot_density

    def generate_boxplot(df):
        FIGURE_SIZE = (10, 6)
        cdf = df[['Total Contribution', 'Fixed Cost', 'Gross Profit', 'Net Profit']]
        cdf_melted = cdf.melt(var_name='Category', value_name='Value')
        plt.figure(figsize=FIGURE_SIZE)
        sns.boxplot(data=cdf_melted, x='Category', y='Value', fill=True, hue='Category')
        plt.title('Boxplot for Fixed Costs, Gross Profit, Contributions, and Net Profit')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_box = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.clf()
        # Inferences
        inferences = {
            'medians': cdf.median().to_dict(),
            'iqr': (cdf.quantile(0.75) - cdf.quantile(0.25)).to_dict(),
            'outliers': {
                'lower_outliers': cdf[
                    cdf < (cdf.quantile(0.25) - 1.5 * (cdf.quantile(0.75) - cdf.quantile(0.25)))].count().to_dict(),
                'upper_outliers': cdf[
                    cdf > (cdf.quantile(0.75) + 1.5 * (cdf.quantile(0.75) - cdf.quantile(0.25)))].count().to_dict(),
            },
        }

        return plot_box, inferences

    def generate_barh_plot(df):
        FIGURE_SIZE = (10, 16)
        corvec = df.corr().iloc[-1].dropna()
        corvec = corvec.drop(['Net Profit', 'Gross Profit', 'Total Contribution'])
        corvec = corvec[~corvec.index.str.contains('contribution', case=False)]
        palette = sns.color_palette("husl", len(corvec))

        plt.figure(figsize=FIGURE_SIZE)
        bars = plt.barh(corvec.index, corvec.values, color=palette, height=0.4)
        for bar in bars:
            xval = bar.get_width()
            plt.text(xval, bar.get_y() + bar.get_height() / 2, round(xval, 2), va='center')
        plt.title('Correlation with Net Profit')
        plt.xlabel('Features')
        plt.ylabel('Correlation Coefficient')

        plt.tight_layout()  # Adjust layout to prevent labels from getting cut off

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')  # Ensure no labels are cut off
        buffer.seek(0)
        plot_barh = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.clf()

        # Positive and Negative correlations
        positive_correlations = corvec[corvec > 0].sort_values(ascending=False).to_dict()
        negative_correlations = corvec[corvec < 0].sort_values().to_dict()

        # Return the plot and the key features
        key_features = {
            'positive_correlations': positive_correlations,
            'negative_correlations': negative_correlations,
        }

        return plot_barh, key_features

    df = dataframe_for_danalysis(request)
    df_columns = list(df.columns)
    for column in ['Gross Profit', 'Fixed Cost', 'Total Contribution', 'Net Profit']:
        if column not in df_columns:
            return None

    plot_histogram, five_num_summary = generate_histogram(df)
    plot_density = generate_density_plot(df)
    plot_box, inferences = generate_boxplot(df)
    plot_barh, key_features = generate_barh_plot(df)
    return plot_histogram, five_num_summary, plot_density, plot_box, inferences, plot_barh, key_features


def d_analysis(request):
    # Generate plots
    visualizations = generate_plots(request)
    plot_flag = False
    if visualizations:
        plot_flag = True
        plot_histogram, five_num_summary, plot_density, plot_box, inferences, plot_barh, key_features = visualizations

    pk = request.session['current_project_id']

    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    project_details = Project.objects.get(pk=pk)
    file_prefix = f"{project_details.project_name}_danalysis_"

    plots = [
        {"title": "Histogram for Net Profit", "data": plot_histogram, "filename": f"{file_prefix}_histogram.png",
         "notes": True},
        {"title": "Distribution Overlay Charts for Fix Costs, Gross Profit, Contributions, and Net Profit",
         "data": plot_density, "filename": f"{file_prefix}_density.png", "notes": False},
        {"title": "Boxplot for Fixed Costs, Gross Profit, Contributions, and Net Profit", "data": plot_box,
         "filename": f"{file_prefix}_box.png", "notes": True},
        {"title": "Correlation of metrics with Net Profit", "data": plot_barh,
         "filename": f"{file_prefix}_corr_bar.png", "notes": True},
    ]

    context = {
        'plots': plots,
        'show_project_navbar': True,
        'plot_flag': plot_flag,
        'five_num_summary': five_num_summary.to_dict(),
        'inferences': inferences,
        'key_features': key_features,
        'current_cycle': current_cycle,
    }

    return render(
        request,
        'd_analysis/d_analysis.html',
        context
    )


@login_required
def employee_add(request):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    current_project_id = request.session.get('current_project_id')
    current_project = Project.objects.get(id=current_project_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee_entry = form.save(commit=False)
            employee_entry.cycle = current_cycle  # Assigning the current user
            employee_entry.project = current_project
            employee_entry.save()
            return redirect('organization_management')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'edit_mode': False,
    }

    return render(
        request,
        'organization_management/employee_add_form.html',
        context
    )


@login_required
def employee_org_edit(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Employee, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('organization_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('organization_management')
    else:
        form = EmployeeForm(instance=entry)

    context = {
        'form': form,
        'edit_mode': True,
    }

    return render(
        request,
        'organization_management/employee_add_form.html',
        context
    )


@login_required
def employee_delete(request, pk):
    current_cycle_id = request.session['current_cycle_id']
    current_cycle = Cycle.objects.get(id=current_cycle_id)

    entry = get_object_or_404(Employee, pk=pk)

    if entry.cycle != current_cycle:
        return redirect('organization_management')  # Redirect if the entry doesn't belong to the current user

    if request.method == 'POST':
        entry.delete()
        return redirect('organization_management')

    context = {
        'entry': entry,
    }

    return render(
        request,
        'organization_management/employee_confirm_delete.html',
        context
    )


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "!#$%&()*+,-.:?@_{}"
    password = ''.join(random.choice(characters) for i in range(length))
    return password


@user_passes_test(is_admin)
def upload_users(request):
    if request.method == 'POST':
        form = UploadUsersForm(request.POST, request.FILES)

        processed_users = []
        processed_projects = []

        if form.is_valid():
            csv_file = request.FILES['user_list']
            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())

            for row in reader:
                project_name = row.get('Team')
                first_name = row.get('First Name')
                last_name = row.get('Last Name')
                email = row.get('BU Email')
                section = row.get('Section')
                password = generate_password()
                username = row.get('Username')

                # Process project
                project_status = ""
                try:
                    project, project_created = Project.objects.get_or_create(
                        project_name=project_name,
                        section=section
                    )

                    if project_created:
                        instantiate_project_start(project)
                        print(f"Created project {project_name}")
                        project_status = "Project Created"
                    else:
                        print(f"Project {project_name} Exists")
                        project_status = "Project Exists"
                except Exception as e:
                    print(f"Project {project_name} Failed")
                    project_status = f"Project Error - {traceback.format_exc()}"
                    traceback.print_exc()
                    continue

                project_details = {
                    'project_name': project_name,
                    'processed': project_status
                }
                processed_projects.append(project_details)

                user_status = ""
                # Process user
                try:
                    user, user_created = User.objects.get_or_create(
                        username=username,
                        password=password,
                        defaults={
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name
                        }
                    )

                    if user_created:
                        user.set_password(password)
                        user.save()
                        print(f"Created project {username}, {email}")
                        user_status = "User Created"
                    else:
                        print(f"Project {username}, {email} Exists")
                        user_status = "User Exists"

                    # Assign user to project
                    project.users.add(user)

                except Exception as e:
                    user_status = f"User Error - {traceback.format_exc()}"
                    print(f"Project {username}, {email} Failed")
                    traceback.print_exc()
                    continue  # Skip to the next user if creation fails
                user_details = {
                    'username': username,
                    'password': password,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'processed': user_status,
                }
                processed_users.append(user_details)

            # Pass the results to the template for display
            context = {
                'processed_users': processed_users,
                'processed_projects': processed_projects,
            }

            request.session['processed_users'] = processed_users
            return render(request, 'admin_utils/user_creation_success.html', context)
    else:
        form = UploadUsersForm()

    context = {
        'form': form,
    }
    return render(request, 'admin_utils/upload_users.html', context)


def download_csv(request):
    processed_records = request.session.get('processed_users', [])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="processed_users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Password', 'First Name', 'Last Name', 'Status'])

    for record in processed_records:
        writer.writerow([
            record['username'],
            record['email'],
            record['password'],
            record['first_name'],
            record['last_name'],
            record['processed']
        ])

    return response


# def email_users(request):
#     if request.method == 'POST':
#         form = Upload(request.POST, request.FILES)
#         processed_records = []
#
#         if form.is_valid():
#             file = request.FILES['user_list']
#             df = pd.read_csv(file)
#
#             for index, row in df.iterrows():
#                 username = row['Username']
#                 password = generate_password()
#
#                 valid_processed = False
#                 if not User.objects.filter(username=username).exists():
#                     try:
#                         User.objects.create_user(
#                             username=row['Username'],
#                             email=row['Email'],
#                             password=password,
#                             first_name=row['First Name'],
#                             last_name=row['Last Name']
#                         )
#
#                         valid_processed = True
#                     except:
#                         valid_processed = False
#
#                 user = {
#                     'username': username,
#                     'password': password,
#                     'email': row['Email'],
#                     'first_name': row['First Name'],
#                     'last_name': row['Last Name'],
#                     'processed': valid_processed,
#                 }
#                 processed_records.append(user)
#
#                 context = {
#                     'processed_records': processed_records,
#                 }
#
#             request.session['processed_records'] = processed_records
#             return render(request, 'admin_utils/user_creation_success.html', context)
#     else:
#         form = UploadUsersForm()
#
#     context = {
#         'form': form,
#     }
#     return render(request, 'admin_utils/upload_users.html', context)


@user_passes_test(is_admin)
def manage_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        user_form = ProjectUserForm(request.POST, project=project)
        project_form = ProjectForm(request.POST, instance=project)

        if 'save_project' in request.POST and project_form.is_valid():
            project_form.save()
            return redirect('manage_project', project_id=project.id)

        if 'add_users' in request.POST and user_form.is_valid():
            users = user_form.cleaned_data['users']
            project.users.add(*users)
            return redirect('manage_project', project_id=project.id)

        if 'remove_users' in request.POST and user_form.is_valid():
            users = user_form.cleaned_data['users']
            project.users.remove(*users)
            return redirect('manage_project', project_id=project.id)
    else:
        user_form = ProjectUserForm(project=project)
        project_form = ProjectForm(instance=project)

    context = {
        'user_form': user_form,
        'project_form': project_form,
        'project': project,
    }

    return render(request, 'admin_utils/manage_project.html', context)


@user_passes_test(is_admin)
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'admin_utils/project_list.html', {'projects': projects})

# Financial statements

from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from b_sim.models import Project, Cycle, SalesProjection, Employee, Rent, Utility, Debt, MarketingEntry, Tax

def financial_statements_view(request):
    # Retrieve the selected cycle from session
    current_cycle_id = request.session.get("current_cycle_id")
    if not current_cycle_id:
        return render(request, "financial_statements/financial_statements.html", {"error": "No cycle selected."})

    # Fetch the current cycle and project
    current_cycle = get_object_or_404(Cycle, id=current_cycle_id)
    project = current_cycle.project

    # Get selected fiscal year (default to Year 1)
    fy = int(request.GET.get("fy", 1))

    # Show balance sheet only for Year 1
    show_balance_sheet = fy == 1

    # Helper function to avoid None values
    def safe_decimal(value):
        return Decimal(value) if value is not None else Decimal(0)

    # Fetch sales data
    sales_data = SalesProjection.objects.filter(project_id=project.id, cycle_id=current_cycle_id, fy=fy).values(
        "product_id", "supply_quantity", "revenue", "expense"
    )

    # Revenue and expenses calculations
    net_sales = sum(safe_decimal(data["revenue"]) for data in sales_data)
    cost_of_sales = sum(safe_decimal(data["expense"]) for data in sales_data)
    gross_profit = net_sales - cost_of_sales

    # Fixed costs calculations
    fixed_costs = {
        "rent": safe_decimal(Rent.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum(f"rent_payment_fy{fy}"))["total"]),
        "salaries": safe_decimal(Employee.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum(f"employee_budget_fy{fy}"))["total"]),
        "utilities": safe_decimal(Utility.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum(f"utility_budget_fy{fy}"))["total"]),
        "marketing": safe_decimal(MarketingEntry.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum(f"payment_fy{fy}_value"))["total"]),
        "loan_payments": safe_decimal(Debt.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum(f"debt_payment_fy{fy}"))["total"]),
        "depreciation": Decimal(7500) if fy == 1 else Decimal(14250 if fy == 2 else 12825)  # Example fixed depreciation
    }

    total_fixed_costs = sum(fixed_costs.values())
    total_expenses = cost_of_sales + total_fixed_costs
    operating_income = gross_profit - total_fixed_costs

    # Tax Calculation (Only if operating income is positive)
    tax_rate = Decimal(0.35)
    tax_expense = operating_income * tax_rate if operating_income > 0 else Decimal(0)
    net_income_after_tax = operating_income - tax_expense

    # Cash Flow Calculation
    beginning_cash_balance = Decimal(0) if fy == 1 else safe_decimal(request.session.get(f"ending_cash_balance_fy{fy-1}", Decimal(0)))
    total_cash_available = beginning_cash_balance + net_sales
    total_cash_paid_out = total_expenses

    # ADD INVESTING ACTIVITIES FOR YEAR 1
    cash_flow_from_investing = Decimal(-150000) if fy == 1 else Decimal(0)

    # Ending Cash Balance Calculation
    ending_cash_balance = total_cash_available - total_cash_paid_out + cash_flow_from_investing

    # Store ending cash balance for the next year
    request.session[f"ending_cash_balance_fy{fy}"] = str(ending_cash_balance)

    # Balance Sheet (Year 1 Only)
    private_investment = Decimal(150000)  # Fixed Investment
    cash = safe_decimal(Debt.objects.filter(project_id=project.id, cycle_id=current_cycle_id).aggregate(total=Sum("debt_amount"))["total"])
    net_machinery_equipment = private_investment

    total_assets = cash + net_machinery_equipment
    total_liabilities = cash
    total_equity = private_investment

    # Context for template
    context = {
        "project": project,
        "cycle": current_cycle.cycle_number,
        "cycle_id": current_cycle_id,
        "fy": fy,
        "show_balance_sheet": show_balance_sheet,
        "net_sales": net_sales,
        "cost_of_sales": cost_of_sales,
        "gross_profit": gross_profit,
        "fixed_costs": fixed_costs,
        "total_fixed_costs": total_fixed_costs,
        "total_expenses": total_expenses,
        "operating_income": operating_income,
        "tax_expense": tax_expense,
        "net_income_after_tax": net_income_after_tax,
        "beginning_cash_balance": beginning_cash_balance,
        "total_cash_available": total_cash_available,
        "total_cash_paid_out": total_cash_paid_out,
        "cash_flow_from_investing": cash_flow_from_investing,
        "ending_cash_balance": ending_cash_balance,
        "cash": cash,
        "net_machinery_equipment": net_machinery_equipment,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
    }

    return render(request, "financial_statements/financial_statements.html", context)

# optimization
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

@csrf_exempt
def optimize_market_size(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    import json
    data = json.loads(request.body)

    try:
        project_id = data['project_id']
        cycle_id = data['cycle_id']
        market_prices = data['market_research_price']
        min_prices = data['min_price']
        max_prices = data['max_price']
        min_deviation = data['min_consumption_deviation']
        max_deviation = data['max_consumption_deviation']
    except KeyError as e:
        return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)

    products = Product.objects.filter(project_id=project_id, cycle_id=cycle_id).order_by('product_id')

    if len(products) != len(market_prices):
        return JsonResponse({'error': 'Number of market prices does not match number of products.'}, status=400)

    product_data = []
    retail_tms = 0
    wholesale_tms = 0

    # Step 1. Pre-calculate tms_base and variable costs
    for idx, product in enumerate(products):
        sales = SalesProjection.objects.filter(product=product, cycle_id=cycle_id, fy=1)
        tms_base = sum(min(float(s.demand_quantity), float(s.supply_quantity)) for s in sales)

        variable_cost = float(product.material_cost + product.labor_cost + product.other_cost)

        elasticity = -1.5 if product.product_distribution == 'retail' else -0.8

        product_data.append({
            'product': product,
            'product_id': product.product_id,
            'product_name': product.product_name,
            'distribution': product.product_distribution,
            'variable_cost': variable_cost,
            'market_price': float(market_prices[idx]),
            'min_price': float(min_prices[idx]),
            'max_price': float(max_prices[idx]),
            'elasticity': elasticity,
            'tms_base': tms_base,
        })

        if product.product_distribution == 'retail':
            retail_tms += tms_base
        else:
            wholesale_tms += tms_base

    # Step 2. Calculate initial profit
    initial_revenue = 0
    initial_expenses = 0
    for p in product_data:
        initial_revenue += p['market_price'] * p['tms_base']
        initial_expenses += p['variable_cost'] * p['tms_base']

    initial_profit = initial_revenue - initial_expenses

    # Step 3. Optimization function
    def objective(prices):
        revenue = 0
        expense = 0
        consumption = 0
        for i, p in enumerate(product_data):
            price = prices[i]
            tms = p['tms_base']
            elasticity = p['elasticity']
            adj_tms = tms * (1 + elasticity * (price - p['market_price']) / p['market_price'])
            revenue += price * adj_tms
            expense += p['variable_cost'] * adj_tms
            consumption += adj_tms

        deviation = (consumption - sum(p['tms_base'] for p in product_data)) / sum(p['tms_base'] for p in product_data)
        if deviation < min_deviation or deviation > max_deviation:
            return 1e10  # Big penalty if out of range

        return -(revenue - expense)  # Maximize profit

    # Step 4. Constraints
    bounds = [(p['min_price'], p['max_price']) for p in product_data]
    x0 = [p['market_price'] for p in product_data]

    result = minimize(objective, x0, bounds=bounds)

    optimized_prices = result.x

    # Step 5. Prepare final output
    retail_sum = 0
    wholesale_sum = 0

    for i, p in enumerate(product_data):
        price = optimized_prices[i]
        adj_tms = p['tms_base'] * (1 + p['elasticity'] * (price - p['market_price']) / p['market_price'])
        p['optimized_price'] = round(price, 2)
        p['adjusted_tms'] = round(adj_tms, 2)

        if p['distribution'] == 'retail':
            retail_sum += adj_tms
        else:
            wholesale_sum += adj_tms

    # Normalize shares
    for p in product_data:
        if p['distribution'] == 'retail' and retail_sum > 0:
            p['normalized_tms_share_percent'] = round(p['adjusted_tms'] / retail_sum * 100, 2)
        elif p['distribution'] == 'wholesale' and wholesale_sum > 0:
            p['normalized_tms_share_percent'] = round(p['adjusted_tms'] / wholesale_sum * 100, 2)
        else:
            p['normalized_tms_share_percent'] = 0

    # Step 6. Calculate optimized profit
    optimized_revenue = sum(p['optimized_price'] * p['adjusted_tms'] for p in product_data)
    optimized_expense = sum(p['variable_cost'] * p['adjusted_tms'] for p in product_data)
    optimized_profit = optimized_revenue - optimized_expense

    response = {
        'initial_net_sales': round(initial_revenue, 2),
        'initial_expenses': round(initial_expenses, 2),
        'initial_gross_profit': round(initial_profit, 2),
        'optimized_net_sales': round(optimized_revenue, 2),
        'optimized_expenses': round(optimized_expense, 2),
        'optimized_gross_profit': round(optimized_profit, 2),
        'distribution_group_share_percent': {
            'retail': 100 if retail_sum > 0 else 0,
            'wholesale': 100 if wholesale_sum > 0 else 0
        },
        'result': [{
            'product_id': str(p['product_id']),
            'product_name': p['product_name'],
            'distribution': p['distribution'],
            'variable_cost': round(p['variable_cost'], 2),
            'market_price': round(p['market_price'], 2),
            'min_price': round(p['min_price'], 2),
            'max_price': round(p['max_price'], 2),
            'optimized_price': p['optimized_price'],
            'elasticity': p['elasticity'],
            'tms_base': round(p['tms_base'], 2),
            'adjusted_tms': p['adjusted_tms'],
            'normalized_tms_share_percent': p['normalized_tms_share_percent'],
        } for p in product_data]
    }

    return JsonResponse(response, safe=False)

from rest_framework.response import Response
@csrf_exempt
@api_view(['POST'])
def optimize_variable_cost(request):
    try:
        data = request.data
        project_id = data.get("project_id")
        cycle_id = data.get("cycle_id")
        elasticities = data.get("elasticities")
        min_variable_costs = data.get("min_variable_cost")
        max_variable_costs = data.get("max_variable_cost")
        min_dev = Decimal(str(data.get("min_consumption_deviation", -0.02)))
        max_dev = Decimal(str(data.get("max_consumption_deviation", 0.02)))

        if not (project_id and cycle_id and elasticities and min_variable_costs and max_variable_costs):
            return JsonResponse({"error": "Missing required fields."}, status=400)

        products = Product.objects.filter(project_id=project_id, cycle_id=cycle_id).order_by('product_id')

        if len(products) != len(elasticities) or len(products) != len(min_variable_costs) or len(products) != len(max_variable_costs):
            return JsonResponse({"error": "Input lists must match number of products."}, status=400)

        result = []
        original_net_sales = Decimal(0)
        original_expenses = Decimal(0)
        optimized_net_sales = Decimal(0)
        optimized_expenses = Decimal(0)

        for idx, product in enumerate(products):
            elasticity = float(elasticities[idx])
            min_cost = float(min_variable_costs[idx])
            max_cost = float(max_variable_costs[idx])

            sales = SalesProjection.objects.filter(product=product, cycle_id=cycle_id, fy=1)
            monthly_values = [min(float(s.demand_quantity), float(s.supply_quantity)) for s in sales]
            tms_base = sum(monthly_values)
            market_price = float(product.price)

            # Original Revenue and Cost
            original_revenue = Decimal(str(market_price)) * Decimal(str(tms_base))
            original_cost = Decimal(str(product.material_cost + product.labor_cost + product.other_cost)) * Decimal(str(tms_base))

            original_net_sales += original_revenue
            original_expenses += original_cost

            # Optimization - maximize profit by adjusting variable cost within bounds
            best_cost = min_cost
            best_profit = -float('inf')
            optimized_tms = tms_base

            for step in range(100):
                trial_cost = min_cost + step * (max_cost - min_cost) / 99
                trial_contribution = market_price - trial_cost

                # Projected Consumption formula (same logic for all distributions)
                adjusted_tms = tms_base * (1 + elasticity * (trial_contribution - (market_price - float(product.material_cost + product.labor_cost + product.other_cost))) / max(market_price, 0.01))
                deviation = (adjusted_tms - tms_base) / max(tms_base, 1)

                if deviation < float(min_dev) or deviation > float(max_dev):
                    continue

                trial_profit = adjusted_tms * (market_price - trial_cost)

                if trial_profit > best_profit:
                    best_profit = trial_profit
                    best_cost = trial_cost
                    optimized_tms = adjusted_tms

            optimized_expense = Decimal(str(best_cost)) * Decimal(str(optimized_tms))
            optimized_revenue = Decimal(str(market_price)) * Decimal(str(optimized_tms))

            optimized_net_sales += optimized_revenue
            optimized_expenses += optimized_expense

            result.append({
                "product_id": str(product.product_id),
                "product_name": product.product_name,
                "distribution": product.product_distribution,
                "market_price": market_price,
                "base_variable_cost": float(product.material_cost + product.labor_cost + product.other_cost),
                "min_variable_cost": min_cost,
                "max_variable_cost": max_cost,
                "optimized_variable_cost": round(best_cost, 2),
                "elasticity": elasticity,
                "tms_base": round(tms_base, 2),
                "adjusted_tms": round(optimized_tms, 2),
            })

        return JsonResponse({
            "result": result,
            "original_net_sales": round(original_net_sales, 2),
            "original_expenses": round(original_expenses, 2),
            "original_profit": round(original_net_sales - original_expenses, 2),
            "optimized_net_sales": round(optimized_net_sales, 2),
            "optimized_expenses": round(optimized_expenses, 2),
            "optimized_profit": round(optimized_net_sales - optimized_expenses, 2),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
