from django.contrib import admin
from .models import Task
from .models import Report

# Register your models here.
admin.site.register(Task)
admin.site.register(Report)