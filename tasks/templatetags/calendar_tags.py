from django import template

register = template.Library()


@register.simple_tag
def get_task_count(day, task_counts_list):
    for date, count in task_counts_list:
        if date == day:
            return count
    return 0
