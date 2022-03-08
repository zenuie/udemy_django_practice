from django import forms
from .models import Reviewrating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviewrating
        fields = ['subject', 'review', 'rating']
