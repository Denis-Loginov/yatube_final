from django import template

# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
register = template.Library()


@register.filter
# применение "декораторов", функций, меняющих поведение функций
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
