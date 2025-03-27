from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from decimal import Decimal

FY_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
]


class Project(models.Model):
    users = models.ManyToManyField(User, related_name='projects')  # Many-to-many relationship with User
    project_name = models.CharField(max_length=255, null=True)
    section = models.CharField(max_length=255, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.project_name


class ProjectStartDefaults(models.Model):
    parameter_units_choice = [
        ('%', '%'),
        ('number', 'number'),
    ]

    parameter_ref = models.CharField(max_length=255)
    parameter_type = models.CharField(max_length=20)
    parameter_num = models.DecimalField(max_digits=10, decimal_places=2)
    parameter_name = models.CharField(max_length=255)
    parameter_unit = models.CharField(max_length=max(len(choice[1]) for choice in parameter_units_choice),
                                      choices=parameter_units_choice)

    def __str__(self):
        return self.parameter_type, self.parameter_num, self.parameter_name


class ProjectStartSettings(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_start_settings')

    is_editable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    # csf 1
    brand_utilization_fy1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    brand_utilization_fy2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    brand_utilization_fy3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    brand_utilization_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # csf 2
    tech_personnel_retention_fy1 = models.IntegerField(null=True, blank=True)
    tech_personnel_retention_fy2 = models.IntegerField(null=True, blank=True)
    tech_personnel_retention_fy3 = models.IntegerField(null=True, blank=True)

    # csf 3
    marketing_personnel_retention_fy1 = models.IntegerField(null=True, blank=True)
    marketing_personnel_retention_fy2 = models.IntegerField(null=True, blank=True)
    marketing_personnel_retention_fy3 = models.IntegerField(null=True, blank=True)

    # kpi 1
    actual_market_size_fy0 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    multiplier_fy1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    multiplier_fy2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    multiplier_fy3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # kpi 2
    number_of_customers = models.IntegerField(null=True, blank=True)

    # kpi 3
    average_consumption_per_customer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # kpi 4
    market_size_without_project_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    market_size_without_project_fy0_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_fy1_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_fy2_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_fy3_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_size_without_project_unit_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # kpi 5
    projected_increase_with_project = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # kpi 6
    projected_annual_sales_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_annual_sales_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_annual_sales_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_annual_sales_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    projected_new_brand_sales_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_new_brand_sales_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_new_brand_sales_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_new_brand_sales_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # kpi 7
    projected_consumption_new_brand_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_consumption_new_brand_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_consumption_new_brand_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_consumption_new_brand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    projected_consumption_new_brand_fy1_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                                                   blank=True)
    projected_consumption_new_brand_fy2_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                                                   blank=True)
    projected_consumption_new_brand_fy3_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                                                   blank=True)
    projected_consumption_new_brand_unit_total = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                                                     blank=True)

    projected_beer_consumption_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_beer_consumption_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    projected_beer_consumption_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    wholesale_distribution_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    wholesale_distribution_fy1_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_fy2_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_fy3_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_distribution_unit_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # kpi 8
    new_technology_capacity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Project Start Record {self.id}, {self.actual_market_size_fy0}"

    def save(self, *args, **kwargs):
        if self.number_of_customers is not None and self.average_consumption_per_customer is not None:
            self.market_size_without_project_fy0_unit = self.number_of_customers * self.average_consumption_per_customer
        else:
            self.market_size_without_project_fy0_unit = None

        if self.market_size_without_project_fy1 is not None and self.market_size_without_project_fy0_unit is not None:
            self.market_size_without_project_fy1_unit = self.market_size_without_project_fy1 / 100 * self.market_size_without_project_fy0_unit
        else:
            self.market_size_without_project_fy1_unit = None

        if self.market_size_without_project_fy2 is not None and self.market_size_without_project_fy0_unit is not None:
            self.market_size_without_project_fy2_unit = self.market_size_without_project_fy2 / 100 * self.market_size_without_project_fy0_unit
        else:
            self.market_size_without_project_fy2_unit = None

        if self.market_size_without_project_fy3 is not None and self.market_size_without_project_fy0_unit is not None:
            self.market_size_without_project_fy3_unit = self.market_size_without_project_fy3 / 100 * self.market_size_without_project_fy0_unit
        else:
            self.market_size_without_project_fy3_unit = None

        if self.market_size_without_project_fy1_unit is not None and self.market_size_without_project_fy2_unit is not None and self.market_size_without_project_fy3_unit is not None:
            self.market_size_without_project_unit_total = self.market_size_without_project_fy1_unit + self.market_size_without_project_fy2_unit + self.market_size_without_project_fy3_unit
        else:
            self.market_size_without_project_unit_total = None

        if self.projected_annual_sales_fy1 is not None and self.projected_annual_sales_fy2 is not None and self.projected_annual_sales_fy3 is not None:
            self.projected_annual_sales_total = self.projected_annual_sales_fy1 + self.projected_annual_sales_fy2 + self.projected_annual_sales_fy3
        else:
            self.projected_annual_sales_total = None

        if self.market_size_without_project_unit_total is not None and self.projected_increase_with_project is not None:
            self.projected_new_brand_sales_total = self.market_size_without_project_unit_total * self.projected_increase_with_project / 100
        else:
            self.projected_new_brand_sales_total = None

        if self.projected_annual_sales_fy1 is not None and self.projected_new_brand_sales_total is not None:
            self.projected_new_brand_sales_fy1 = self.projected_new_brand_sales_total * self.projected_annual_sales_fy1 / 100
        else:
            self.projected_new_brand_sales_fy1 = None

        if self.projected_annual_sales_fy2 is not None and self.projected_new_brand_sales_total is not None:
            self.projected_new_brand_sales_fy2 = self.projected_new_brand_sales_total * self.projected_annual_sales_fy2 / 100
        else:
            self.projected_annual_sales_fy2 = None

        if self.projected_annual_sales_fy3 is not None and self.projected_new_brand_sales_total is not None:
            self.projected_new_brand_sales_fy3 = self.projected_new_brand_sales_total * self.projected_annual_sales_fy3 / 100
        else:
            self.projected_new_brand_sales_fy3 = None

        if self.projected_new_brand_sales_fy1 is not None and self.projected_consumption_new_brand_fy1 is not None:
            self.projected_consumption_new_brand_fy1_unit = self.projected_consumption_new_brand_fy1 / 100 * self.projected_new_brand_sales_fy1
        else:
            self.projected_consumption_new_brand_fy1_unit = None

        if self.projected_new_brand_sales_fy2 is not None and self.projected_consumption_new_brand_fy2 is not None:
            self.projected_consumption_new_brand_fy2_unit = self.projected_consumption_new_brand_fy2 / 100 * self.projected_new_brand_sales_fy2
        else:
            self.projected_consumption_new_brand_fy2_unit = None

        if self.projected_new_brand_sales_fy3 is not None and self.projected_consumption_new_brand_fy3 is not None:
            self.projected_consumption_new_brand_fy3_unit = self.projected_consumption_new_brand_fy3 / 100 * self.projected_new_brand_sales_fy3
        else:
            self.projected_consumption_new_brand_fy3_unit = None

        if self.projected_consumption_new_brand_fy1_unit is not None and self.projected_consumption_new_brand_fy2_unit is not None and self.projected_consumption_new_brand_fy3_unit is not None:
            self.projected_consumption_new_brand_unit_total = self.projected_consumption_new_brand_fy1_unit + self.projected_consumption_new_brand_fy2_unit + self.projected_consumption_new_brand_fy3_unit
        else:
            self.projected_consumption_new_brand_unit_total = None

        if self.projected_consumption_new_brand_unit_total is not None and self.projected_new_brand_sales_total is not None:
            self.projected_consumption_new_brand_total = self.projected_consumption_new_brand_unit_total / self.projected_new_brand_sales_total
        else:
            self.projected_consumption_new_brand_total = None

        if self.market_size_without_project_fy1_unit is not None and self.projected_consumption_new_brand_fy1_unit is not None:
            self.projected_beer_consumption_fy1 = self.projected_consumption_new_brand_fy1_unit / self.market_size_without_project_fy1_unit
        else:
            self.projected_beer_consumption_fy1 = None

        if self.market_size_without_project_fy2_unit is not None and self.projected_consumption_new_brand_fy2_unit is not None:
            self.projected_beer_consumption_fy2 = self.projected_consumption_new_brand_fy2_unit / self.market_size_without_project_fy2_unit
        else:
            self.projected_beer_consumption_fy2 = None

        if self.market_size_without_project_fy3_unit is not None and self.projected_consumption_new_brand_fy3_unit is not None:
            self.projected_beer_consumption_fy3 = self.projected_consumption_new_brand_fy3_unit / self.market_size_without_project_fy3_unit
        else:
            self.projected_beer_consumption_fy3 = None

        if self.projected_consumption_new_brand_fy1 is not None:
            self.wholesale_distribution_fy1 = 100 - self.projected_consumption_new_brand_fy1
        else:
            self.wholesale_distribution_fy1 = None

        if self.projected_consumption_new_brand_fy2 is not None:
            self.wholesale_distribution_fy2 = 100 - self.projected_consumption_new_brand_fy2
        else:
            self.wholesale_distribution_fy2 = None

        if self.projected_consumption_new_brand_fy3 is not None:
            self.wholesale_distribution_fy3 = 100 - self.projected_consumption_new_brand_fy3
        else:
            self.wholesale_distribution_fy3 = None

        if self.wholesale_distribution_fy1 is not None and self.projected_new_brand_sales_fy1 is not None:
            self.wholesale_distribution_fy1_unit = self.wholesale_distribution_fy1 / 100 * self.projected_new_brand_sales_fy1
        else:
            self.wholesale_distribution_fy1_unit = None

        if self.wholesale_distribution_fy2 is not None and self.projected_new_brand_sales_fy2 is not None:
            self.wholesale_distribution_fy2_unit = self.wholesale_distribution_fy2 / 100 * self.projected_new_brand_sales_fy2
        else:
            self.wholesale_distribution_fy2_unit = None

        if self.wholesale_distribution_fy3 is not None and self.projected_new_brand_sales_fy3 is not None:
            self.wholesale_distribution_fy3_unit = self.wholesale_distribution_fy3 / 100 * self.projected_new_brand_sales_fy3
        else:
            self.wholesale_distribution_fy3_unit = None

        if self.wholesale_distribution_fy1_unit is not None and self.wholesale_distribution_fy1_unit is not None and self.wholesale_distribution_fy1_unit is not None:
            self.wholesale_distribution_unit_total = self.wholesale_distribution_fy1_unit + self.wholesale_distribution_fy2_unit + self.wholesale_distribution_fy3_unit
        else:
            self.wholesale_distribution_unit_total = None

        if self.wholesale_distribution_unit_total is not None and self.projected_new_brand_sales_total is not None:
            self.wholesale_distribution_total = self.wholesale_distribution_unit_total / self.projected_new_brand_sales_total
        else:
            self.wholesale_distribution_total = None

        if self.projected_new_brand_sales_fy1 is not None and self.new_technology_capacity is not None:
            self.brand_utilization_fy1 = self.projected_new_brand_sales_fy1 / self.new_technology_capacity
        else:
            self.brand_utilization_fy1 = None

        if self.projected_new_brand_sales_fy2 is not None and self.new_technology_capacity is not None:
            self.brand_utilization_fy2 = self.projected_new_brand_sales_fy2 / self.new_technology_capacity
        else:
            self.brand_utilization_fy2 = None

        if self.projected_new_brand_sales_fy3 is not None and self.new_technology_capacity is not None:
            self.brand_utilization_fy3 = self.projected_new_brand_sales_fy3 / self.new_technology_capacity
        else:
            self.brand_utilization_fy3 = None

        if self.projected_new_brand_sales_total is not None and self.new_technology_capacity is not None:
            self.brand_utilization_total = self.projected_new_brand_sales_total / (3 * self.new_technology_capacity)
        else:
            self.brand_utilization_total = None

        super().save(*args, **kwargs)


class Cycle(models.Model):
    cycle_choice = [
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Operation', 'Operation'),
        ('Innovation', 'Innovation'),
        ('Organization', 'Organization'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cycles')
    cycle_name = models.CharField(max_length=max(len(choice[1]) for choice in cycle_choice),
                                  choices=cycle_choice,
                                  default='retail')
    cycle_number = models.IntegerField(editable=False, null=True)  # Auto-assigned as an integer
    underlying_cycle = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='subsequent_cycles')

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:  # Check if this is a new object being created
            # Get the maximum cycle_number in the current project, default to 0 if none found
            max_number = (self.project.cycles.aggregate(Max('cycle_number'))['cycle_number__max']) or 0
            self.cycle_number = max_number + 1

        super().save(*args, **kwargs)

    def __str__(self):
        # This will change the string representation in forms and admin
        return f"Cycle {self.cycle_number}: {self.cycle_name}"


class Product(models.Model):
    distribution_choices = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('special_offer', 'Special Offer'),
    ]

    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='product')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='marketing_product')

    product_pk = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=10)
    product_name = models.CharField(max_length=100)
    product_distribution = models.CharField(max_length=max(len(choice[1]) for choice in distribution_choices),
                                            choices=distribution_choices,
                                            default='retail')

    # cost
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2)

    # pricing & quantity
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cutoff = models.DecimalField(max_digits=3, decimal_places=2)
    units = models.DecimalField(max_digits=10, decimal_places=2)

    # target market size
    target_market_sizes = models.ManyToManyField('TargetMarketSize', related_name='products')
    sales_projections = models.ManyToManyField('SalesProjection', related_name='products')

    # #for optimization
    # price_elasticity = models.DecimalField(max_digits=5, decimal_places=2, default=-1.0)
    # market_research_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    #
    # min_price_pct = models.DecimalField(max_digits=4, decimal_places=2, default=0.8)  # 80%
    # max_price_pct = models.DecimalField(max_digits=4, decimal_places=2, default=1.2)  # 120%

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.product_name}"


class SalesProjection(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_projection')
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='sales_projection')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sales_projection_project')

    fy = models.IntegerField(choices=FY_CHOICES, default=1)
    month = models.CharField(max_length=3, null=True, default=0)  # Abbreviated month name (e.g., Jan, Feb, etc.)
    projection = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    demand_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Added field
    tank_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Added field
    supply_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Added field

    revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.product} - {self.fy} - {self.month}: {self.projection}"

    def save(self, *args, **kwargs):
        def find_tank_quantity(quantity, cutoff, capacity=1240):
            demand_qty = quantity / capacity
            num_tanks = int(demand_qty)
            if demand_qty - num_tanks >= cutoff:
                num_tanks += 1
            return num_tanks

        # Calculate demand_quantity only if tms_value and projection are available
        try:
            tms = self.product.targeted_market_size.get(fy=self.fy)

            cost = self.product.material_cost + self.product.labor_cost + self.product.other_cost
            price = self.product.price

            if tms.tms_value is not None and self.projection is not None:
                demand_quantity = tms.tms_value * Decimal(self.projection / 100)
                tank_quantity = find_tank_quantity(demand_quantity, self.product.cutoff)
                supply_quantity = tank_quantity * 1240

                revenue = supply_quantity * price
                expense = supply_quantity * cost
                contribution = revenue - expense
            else:
                print("TMS Value or Projection is None")
                demand_quantity = None
                tank_quantity = None
                supply_quantity = None
                revenue = None
                expense = None
                contribution = None
        except:
            import traceback
            traceback.print_exc()
            print("Error in finding TMS Value or Projection")
            demand_quantity = None
            tank_quantity = None
            supply_quantity = None
            revenue = None
            expense = None
            contribution = None

        self.demand_quantity = demand_quantity
        self.tank_quantity = tank_quantity
        self.supply_quantity = supply_quantity
        self.revenue = revenue
        self.expense = expense
        self.contribution = contribution

        super().save(*args, **kwargs)


class MarketingEntry(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='marketing_costs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='marketing_project')

    name = models.CharField(max_length=35)
    payment_fy1_value = models.FloatField()
    payment_fy2_multiplier = models.FloatField()
    payment_fy2_value = models.FloatField()
    payment_fy3_multiplier = models.FloatField()
    payment_fy3_value = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        payment_fy2_value = self.payment_fy1_value * self.payment_fy2_multiplier
        payment_fy3_value = payment_fy2_value * self.payment_fy3_multiplier

        self.payment_fy2_value = round(payment_fy2_value, 2)
        self.payment_fy3_value = round(payment_fy3_value, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TargetMarketSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='targeted_market_size')
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='targeted_market_size_cycle')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tms_project')

    fy = models.IntegerField(choices=FY_CHOICES, default=1)
    tms_pct = models.DecimalField(max_digits=5, decimal_places=2)
    tms_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['fy']
        unique_together = [['product', 'fy']]

    def __str__(self):
        return f"{self.product.product_name} - {self.fy}"

    def save(self, *args, **kwargs):
        project_start = ProjectStartSettings.objects.filter(project=self.project).first()

        wholesale_multiplier = {
            '1': project_start.wholesale_distribution_fy1_unit,
            '2': project_start.wholesale_distribution_fy2_unit,
            '3': project_start.wholesale_distribution_fy3_unit,
        }

        retail_multiplier = {
            '1': project_start.projected_consumption_new_brand_fy1_unit,
            '2': project_start.projected_consumption_new_brand_fy2_unit,
            '3': project_start.projected_consumption_new_brand_fy3_unit,
        }

        # Get the multiplier for the specified fy, or use a default value if fy is not found
        if self.product.product_distribution == "retail":
            targeted_market_size_total = retail_multiplier.get(str(self.fy), Decimal(0))
        elif self.product.product_distribution == "wholesale":
            targeted_market_size_total = wholesale_multiplier.get(str(self.fy), Decimal(0))

        if self.tms_pct:
            # Convert tms_pct to a proportion if it's stored as a percentage
            self.tms_value = Decimal(self.tms_pct / 100) * targeted_market_size_total

        super().save(*args, **kwargs)

        related_sales_projections = SalesProjection.objects.filter(
            product=self.product,
            cycle=self.cycle,
            project=self.project,
            fy=self.fy,
        )

        for projection in related_sales_projections:
            projection.save()


# Financial Management
class FinancialManagement(models.Model):
    fin_entry = models.TextField()
    fin_type = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.fin_entry, self.fin_type


class Employee(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='employee')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='employee_project')

    employee_position = models.CharField(max_length=35)
    employee_budget_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    employee_num = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    employee_fy2_multiplier = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    employee_budget_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    employee_fy3_multiplier = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    employee_budget_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if self.employee_fy2_multiplier and self.employee_fy3_multiplier:
            employee_budget_fy2 = self.employee_budget_fy1 * self.employee_fy2_multiplier
            employee_budget_fy3 = employee_budget_fy2 * self.employee_fy3_multiplier

            self.employee_budget_fy2 = round(employee_budget_fy2, 2)
            self.employee_budget_fy3 = round(employee_budget_fy3, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee_position


class Utility(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='utility')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='utility_project')

    utility_name = models.CharField(max_length=35)

    utility_budget_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    utility_multiplier_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    utility_budget_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    utility_multiplier_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    utility_budget_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if self.utility_multiplier_fy2 and self.utility_multiplier_fy3:
            utility_budget_fy2 = self.utility_budget_fy1 * self.utility_multiplier_fy2
            utility_budget_fy3 = utility_budget_fy2 * self.utility_multiplier_fy3

            self.utility_budget_fy2 = round(utility_budget_fy2, 2)
            self.utility_budget_fy3 = round(utility_budget_fy3, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.utility_name


class Rent(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='rent')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='rent_project')

    rent_name = models.CharField(max_length=35)
    rent_area = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    rent_payment_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    rent_multiplier_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rent_payment_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    rent_multiplier_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rent_payment_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if self.rent_multiplier_fy2 and self.rent_multiplier_fy3:
            rent_payment_fy2 = self.rent_payment_fy1 * self.rent_multiplier_fy3
            rent_payment_fy3 = rent_payment_fy2 * self.rent_multiplier_fy3

            self.rent_payment_fy2 = round(rent_payment_fy2, 2)
            self.rent_payment_fy3 = round(rent_payment_fy3, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.rent_name


class Tax(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='tax')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tax_project')

    tax_type = models.CharField(max_length=35)
    tax_pct = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.tax_type


def calculate_loan_payments(principal, annual_interest_rate, months):
    """
    Calculate the monthly and annual loan payments.

    Args:
    principal (float): The loan amount.
    annual_interest_rate (float): The annual interest rate (as a percentage).
    months (int): The loan term in months.

    Returns:
    dict: A dictionary containing the monthly payment and the annual payment.
    """
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    num_payments = months

    # Calculate the monthly payment using the loan payment formula
    monthly_payment = (principal * monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
            (1 + monthly_interest_rate) ** num_payments - 1)

    # Calculate the annual payment
    annual_payment = monthly_payment * 12

    return annual_payment


class Debt(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='debt')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='debt_project')

    debt_name = models.CharField(max_length=35)
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_interest_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_length = models.IntegerField(null=True)
    debt_num_payments = models.IntegerField(null=True)
    debt_start_date = models.TextField(null=True)

    debt_payment_fy1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_payment_fy2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_payment_fy3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if self.debt_amount and self.debt_interest_rate and self.debt_length and self.debt_num_payments:
            debt_payment = calculate_loan_payments(self.debt_amount, self.debt_interest_rate, self.debt_length)

            self.debt_payment_fy1 = debt_payment
            self.debt_payment_fy2 = debt_payment
            self.debt_payment_fy3 = debt_payment

        # if self.debt_amount and self.debt_interest_rate and self.debt_length and self.debt_num_payments:
        #     debt_payment = (round(
        #         self.debt_amount * self.debt_interest_rate * self.debt_length / 100, 2)) / 3  # Formula to be changed
        #
        #     self.debt_payment_fy1 = debt_payment
        #     self.debt_payment_fy2 = debt_payment
        #     self.debt_payment_fy3 = debt_payment

        super().save(*args, **kwargs)

    def __str__(self):
        return self.debt_name


class FinancialMarketIndicator(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='financial_market_indicator')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='financial_market_indicator_project')

    name = models.CharField(max_length=35)
    pct = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

# Nurs
# class FinancialStatement(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="financial_statements")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="financial_statements")
#     cycle = models.IntegerField()  # Assuming cycle is represented as an integer
#     statement_type = models.CharField(max_length=50, choices=[
#         ("balance_sheet", "Balance Sheet"),
#         ("income_statement", "Income Statement"),
#         ("cash_flow", "Cash Flow Statement")
#     ])
#     data = models.JSONField()  # Store financial data dynamically
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.project.project_name} - {self.statement_type} - Cycle {self.cycle}"



