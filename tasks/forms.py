from django import forms
from .models import Task

# Crispy forms helper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Task
        fields = ['title', 'due_date', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Task title'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crispy helper to control layout and CSS classes for responsiveness
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_method = 'post'
        self.helper.form_class = 'task-create-helper'
        # assign CSS classes to individual fields so the template CSS can size them
        self.fields['title'].widget.attrs.update({'class': 'form-control title-field'})
        self.fields['due_date'].widget.attrs.update({'class': 'form-control date-field'})
        self.fields['category'].widget.attrs.update({'class': 'form-select category-field'})
        # Layout (crispy will render fields in this order)
        self.helper.layout = Layout(
            Field('title', css_class='title-field'),
            Field('due_date', css_class='date-field'),
            Field('category', css_class='category-field'),
        )
