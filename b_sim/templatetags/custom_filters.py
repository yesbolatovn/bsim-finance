from django import template

register = template.Library()


@register.filter
def get_by_key(value, arg):
    """Retrieve a value from a dictionary by a dynamic key."""
    return value.get(arg, None)


@register.filter(name='sum_column')
def sum_column(values_list, attribute_name):
    """Sums the attribute named `attribute_name` across a list of objects, treating None as 0."""
    return sum(getattr(item, attribute_name, 0) or 0 for item in values_list)


@register.filter(name='sum_column')
def sum_column_multiplier(values_list, attribute_name):
    """Sums the attribute named `attribute_name` across a list of objects, treating None as 0."""
    return sum(getattr(item, attribute_name, 0) or 0 for item in values_list)


@register.filter(name='get_projection')
def get_projection(sales_projections, month):
    return next((sp for sp in sales_projections if sp.month == month), None)


@register.filter(name='add')
def mul(value, arg):
    return value + arg


@register.filter
def is_tuple(value):
    return isinstance(value, tuple)


@register.filter
def intcomma_and_percentage(value, row):
    try:
        # Check if "percentage" exists in the row
        contains_percentage = "%" in row

        contains_units = "units" in row

        if contains_units:
            return "{:,.0f}".format(round(value))
        else:
            value = float(value)

            # Format the number with comma separators
            if value.is_integer():
                # If the number is an integer, format without decimal places
                formatted_value = "{:,.0f}".format(value)
            else:
                # If the number has decimal places, format with them
                formatted_value = "{:,.2f}".format(value)

            # Append percentage symbol if the unit is "percentage"
            if contains_percentage:
                formatted_value += '%'

        return formatted_value
    except (ValueError, TypeError):
        return value


@register.filter
def format_number(value):
    try:
        value = float(value)
        formatted_value = "{:,.2f}".format(value) if value.is_integer() else "{:,.2f}".format(value)
        return formatted_value.rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return value


@register.filter
def replace_perc(value, arg):
    """
    This replaces all occurrences of `arg` in the given string with ' percentile'.
    """
    if not isinstance(value, str):
        return value
    return value.replace(arg, ' percentile')


@register.filter
def get_by_index(list_, index):
    try:
        return list_[index]
    except IndexError:
        return None


@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value
