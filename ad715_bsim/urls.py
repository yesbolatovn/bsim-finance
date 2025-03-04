"""
URL configuration for ad715_bsim project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from b_sim import views
from b_sim.views import financial_statements_view
from dashboards.views import financial_dashboards_view

urlpatterns = [
    path('', views.signin_page, name='signin_page'),
    path('signin_page/', views.signin_page, name='signin_page'),
    # path('signup_page/', views.signup_page, name='signup_page'),
    path('logout/', views.signout_page, name='logout'),
    path('success/', views.success, name='success'),

    path('change_password/', views.change_password, name='change_password'),
    path('change_password_as_admin/', views.change_password_as_admin, name='change_password_as_admin'),

    path('project_home/', views.project_home, name='project_home'),
    path('project_start/', views.project_start, name='project_start'),

    path('project_start_display/', views.project_start_display, name='project_start_display'),
    # path('create_all_users/', views.create_all_users, name='create_all_users'),


    # path('project_start_form/<int:pk>/', views.project_start_form, name='project_start_form'),

    # marketing management urls:
    path('marketing_management/', views.marketing_management, name='marketing_management'),
    path('marketing_cost_add/', views.marketing_cost_add, name='marketing_cost_add'),
    path('marketing_cost_edit/<int:pk>/', views.marketing_cost_edit, name='marketing_cost_edit'),
    path('marketing_cost_delete/<int:pk>/', views.marketing_cost_delete, name='marketing_cost_delete'),

    path('employee_add/', views.employee_add, name='employee_add'),
    path('employee_org_edit/<int:pk>/', views.employee_org_edit, name='employee_org_edit'),
    path('employee_delete/<int:pk>/', views.employee_delete, name='employee_delete'),

    # innovation management urls:
    path('innovation_management/', views.innovation_management, name='innovation_management'),

    # organization management urls:
    path('organization_management/', views.organization_management, name='organization_management'),

    # operations management urls:
    path('operations_management/', views.operations_management, name='operations_management'),

    path('product_add/', views.product_add, name='product_add'),
    path('product_edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('product_delete/<int:pk>/', views.product_delete, name='product_delete'),

    path('financial_management/', views.financial_management, name='financial_management'),
    path('employee_edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('utility_edit/<int:pk>/', views.utility_edit, name='utility_edit'),
    path('rent_edit/<int:pk>/', views.rent_edit, name='rent_edit'),
    path('tax_edit/<int:pk>/', views.tax_edit, name='tax_edit'),
    path('fmi_edit/<int:pk>/', views.fmi_edit, name='fmi_edit'),

    path('debt_add/', views.debt_add, name='debt_add'),
    path('debt_edit/<int:pk>/', views.debt_edit, name='debt_edit'),
    path('debt_delete/<int:pk>/', views.debt_delete, name='debt_delete'),

    path('targeted_marketsize_edit/<int:pk>/', views.targeted_marketsize_edit, name='targeted_marketsize_edit'),

    path('sales_projections/edit/<int:pk>/<str:fy>/', views.sales_projection_edit, name='sales_projection_edit'),

    path('set_financial_year/', views.set_financial_year, name='set_financial_year'),

    path('project_dashboard', views.project_dashboard, name='project_dashboard'),
    path('select_project/<int:pk>/', views.select_project, name='select_project'),

    path('cycle_dashboard/', views.cycle_dashboard, name='cycle_dashboard'),
    path('cycle_home/', views.cycle_home, name='cycle_home'),
    path('select_cycle/<int:pk>/', views.select_cycle, name='select_cycle'),
    path('sim_nav_page/', views.sim_nav_page, name='sim_nav_page'),
    path('help_page/', views.help_page, name='help_page'),
    path('how_to_play/', views.how_to_play, name='how_to_play'),

    path('create_project/', views.create_project, name='create_project'),
    path('manage_project_users/<int:project_id>/', views.manage_project_users, name='manage_project_users'),

    # path('create_all_users/', views.create_all_users, name='create_all_users'),

    # path('admin-page/<int:project_id>/', views.admin, name='manage_project_users'),

    path('pro_forma/', views.pro_forma, name='pro_forma'),

    path('compare_cycles/', views.compare_cycles, name='compare_cycles'),
    path('sim_report/', views.sim_report, name='sim_report'),


    path('d_analysis/', views.d_analysis, name='d_analysis'),

    path('delete_cycle_view/', views.delete_cycle_view, name='delete_cycle_view'),

    path('upload_users/', views.upload_users, name='upload_users'),
    path('success/', views.success, name='success'),

    path('download_csv/', views.download_csv, name='download_csv'),

    path('project_list/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/manage/', views.manage_project, name='manage_project'),

    # for fin tables
    path('project/statements/', financial_statements_view, name='financial_statements'),
    #path('project/<int:project_id>/statements/', financial_statements_view, name='financial_statements'),


    #For the fin dashboards
    path("django_plotly_dash/", include("django_plotly_dash.urls")),

    # Financial Dashboards with Required Parameters (Project & Cycle)
    path("dashboards/<int:project_id>/<int:cycle_id>/", financial_dashboards_view, name="financial_dashboards"),

]
