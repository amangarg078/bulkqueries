from django import forms


class CodeForm(forms.Form):
    total_codes_to_generate = forms.IntegerField()
