# campaigns/forms.py
from django import forms

class LinkedinLoginForm(forms.Form):
    linkedin_email = forms.EmailField(
        label="LinkedIn Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'})
    )
    linkedin_password = forms.CharField(
        label="LinkedIn Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    domain = forms.CharField(
        label="Domain or Interest",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., AI, Marketing, SaaS'})
    )