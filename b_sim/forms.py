from django import forms
from django.contrib.auth.models import User
from .models import MarketingEntry, Product, TargetMarketSize, SalesProjection, Employee, Utility, Rent, Tax, \
    FinancialMarketIndicator, Cycle, Project, Debt, ProjectStartSettings


class ProjectStartForm(forms.ModelForm):
    class Meta:
        model = ProjectStartSettings
        exclude = ['project']
        fields = [
            'actual_market_size_fy0', 'multiplier_fy1', 'multiplier_fy2', 'multiplier_fy3',
            'number_of_customers', 'average_consumption_per_customer',
            'market_size_without_project_fy1', 'market_size_without_project_fy2', 'market_size_without_project_fy3',
            'projected_increase_with_project',
            'projected_annual_sales_fy1', 'projected_annual_sales_fy2', 'projected_annual_sales_fy3',
            'projected_consumption_new_brand_fy1', 'projected_consumption_new_brand_fy2',
            'projected_consumption_new_brand_fy3',
            'new_technology_capacity',
            'tech_personnel_retention_fy1',
            'tech_personnel_retention_fy2',
            'tech_personnel_retention_fy3',
            'marketing_personnel_retention_fy1',
            'marketing_personnel_retention_fy2',
            'marketing_personnel_retention_fy3',
        ]
        widgets = {
            'actual_market_size_fy0': forms.NumberInput(attrs={'required': True}),
            'multiplier_fy1': forms.NumberInput(attrs={'required': True}),
            'multiplier_fy2': forms.NumberInput(attrs={'required': True}),
            'multiplier_fy3': forms.NumberInput(attrs={'required': True}),
            'number_of_customers': forms.NumberInput(attrs={'required': True}),
            'average_consumption_per_customer': forms.NumberInput(attrs={'required': True}),
            'market_size_without_project_fy1': forms.NumberInput(attrs={'required': True}),
            'market_size_without_project_fy2': forms.NumberInput(attrs={'required': True}),
            'market_size_without_project_fy3': forms.NumberInput(attrs={'required': True}),
            'projected_increase_with_project': forms.NumberInput(attrs={'required': True}),
            'projected_annual_sales_fy1': forms.NumberInput(attrs={'required': True}),
            'projected_annual_sales_fy2': forms.NumberInput(attrs={'required': True}),
            'projected_annual_sales_fy3': forms.NumberInput(attrs={'required': True}),
            'projected_consumption_new_brand_fy1': forms.NumberInput(attrs={'required': True}),
            'projected_consumption_new_brand_fy2': forms.NumberInput(attrs={'required': True}),
            'projected_consumption_new_brand_fy3': forms.NumberInput(attrs={'required': True}),
            'new_technology_capacity': forms.NumberInput(attrs={'required': True}),
            'tech_personnel_retention_fy1': forms.NumberInput(attrs={'required': True}),
            'tech_personnel_retention_fy2': forms.NumberInput(attrs={'required': True}),
            'tech_personnel_retention_fy3': forms.NumberInput(attrs={'required': True}),
            'marketing_personnel_retention_fy1': forms.NumberInput(attrs={'required': True}),
            'marketing_personnel_retention_fy2': forms.NumberInput(attrs={'required': True}),
            'marketing_personnel_retention_fy3': forms.NumberInput(attrs={'required': True}),
        }


class UploadUsersForm(forms.Form):
    user_list = forms.FileField()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'section']  # Include any other fields you want to be editable


class ProjectUserForm(forms.Form):
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all().order_by('username'),
                                           widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super(ProjectUserForm, self).__init__(*args, **kwargs)
        if project:
            self.fields['users'].initial = project.users.all().order_by('username')


class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['cycle_name', 'cycle_number', 'underlying_cycle']

        exclude = ['cycle_number']

    def __init__(self, *args, **kwargs):
        # Expecting project_id to be passed explicitly when the form is instantiated
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)

        # Dynamically set the queryset for the 'underlying_cycle' field based on the project
        if project_id is not None:
            self.fields['underlying_cycle'].queryset = Cycle.objects.filter(project_id=project_id)
        else:
            self.fields['underlying_cycle'].queryset = Cycle.objects.none()

        # Optionally, set empty label for better user experience
        self.fields['underlying_cycle'].empty_label = "Select if applicable"


class MarketingEntryForm(forms.ModelForm):
    class Meta:
        model = MarketingEntry

        fields = ['name',
                  'payment_fy1_value',
                  'payment_fy2_multiplier',
                  'payment_fy3_multiplier', ]

        exclude = ['User']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            'product_id', 'product_name',
            'product_distribution', 'material_cost', 'labor_cost', 'other_cost',
            'price', 'units', 'cutoff',
        ]

        exclude = ['product_pk', 'tms_fy1', 'tms_fy2', 'tms_fy3',
                   'sales_projections_jan', 'sales_projections_feb', 'sales_projections_mar',
                   'sales_projections_apr', 'sales_projections_may', 'sales_projections_jun',
                   'sales_projections_jul', 'sales_projections_aug', 'sales_projections_sep',
                   'sales_projections_oct', 'sales_projections_nov', 'sales_projections_dec', ]

        labels = {
            'product_id': 'Product ID',
            'product_name': 'Product Name',
            'product_distribution': 'Product Distribution',
            'material_cost': 'Material Cost',
            'labor_cost': 'Labor Cost',
            'other_cost': 'Other Cost',
            'price': 'Price',
            'units': 'Units',
            'cutoff': 'Cutoff',
        }


class CycleDeleteForm(forms.Form):
    cycle_id = forms.IntegerField(label='Cycle ID', required=True)


class CycleComparisonForm(forms.Form):
    cycles = forms.ModelMultipleChoiceField(queryset=Cycle.objects.none(), widget=forms.CheckboxSelectMultiple,
                                            required=True)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super(CycleComparisonForm, self).__init__(*args, **kwargs)
        if project:
            self.fields['cycles'].queryset = Cycle.objects.filter(project=project).order_by('cycle_number')


class CustomPasswordChangeForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    old_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        return cleaned_data


class TargetMarketSizeForm(forms.ModelForm):
    class Meta:
        model = TargetMarketSize
        fields = ['tms_pct']

    exclude = [
        'id',
    ]


class SalesProjectionForm(forms.ModelForm):
    class Meta:
        model = SalesProjection
        fields = ['projection']

    exclude = [
        'id',
    ]


# Financial Management
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_position',
            'employee_budget_fy1',
            'employee_num',
            'employee_fy2_multiplier',
            'employee_fy3_multiplier',
        ]
        exclude = [
            'cycle',
        ]


class EmployeeEntryForm(forms.ModelForm):
    class Meta:
        model = Employee

        fields = [
            'employee_position',
            'employee_budget_fy1',
            'employee_num',
            'employee_fy2_multiplier',
            'employee_fy3_multiplier',
        ]
        exclude = [
            'cycle',
        ]


class UtilityForm(forms.ModelForm):
    class Meta:
        model = Utility
        fields = [
            'utility_name',
            'utility_budget_fy1',
            'utility_multiplier_fy2',
            'utility_multiplier_fy3',
        ]
        exclude = [
            'cycle',
        ]


class RentForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = [
            'rent_name',
            'rent_area',
            'rent_payment_fy1',
            'rent_multiplier_fy2',
            'rent_multiplier_fy3',
        ]
        exclude = [
            'cycle',
        ]


class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = [
            'tax_type',
            'tax_pct',
        ]
        exclude = [
            'cycle',
        ]


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = [
            'debt_name',
            'debt_amount',
            'debt_interest_rate',
            'debt_length',
            'debt_num_payments',
        ]
        exclude = [
            'cycle',
            'project',
            'debt_payment_fy1',
            'debt_payment_fy2',
            'debt_payment_fy3',
            'debt_start_date',
        ]


class FMIForm(forms.ModelForm):
    class Meta:
        model = FinancialMarketIndicator
        fields = [
            'name',
            'pct',
        ]
        exclude = [
            'cycle',
        ]
