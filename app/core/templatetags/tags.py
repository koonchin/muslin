from django import template

register = template.Library()


@register.filter
def split_string(value, delimiter):
    parts = value.split(delimiter)
    return parts[1]
