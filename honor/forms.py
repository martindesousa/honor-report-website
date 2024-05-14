from django import forms
from .models import Task
from .models import Report

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['nameOfOffender', 'description']
