from django import forms
from .models import Organization, FinancialPeriod, FinancialEntry, BudgetLine, Scenario, Client, WorkspaceDocument
class OrganizationForm(forms.ModelForm):
 class Meta: model=Organization; fields=["name","industry","currency","financial_year_start_month","gstin"]
class PeriodForm(forms.ModelForm):
 class Meta: model=FinancialPeriod; fields=["organization","name","start_date","end_date","is_actual"]; widgets={"start_date":forms.DateInput(attrs={"type":"date"}),"end_date":forms.DateInput(attrs={"type":"date"})}
class EntryForm(forms.ModelForm):
 class Meta: model=FinancialEntry; fields=["organization","period","category","label","amount","department","segment","customer"]
class BudgetForm(forms.ModelForm):
 class Meta: model=BudgetLine; fields=["organization","period","category","label","budget_amount","department"]
class ScenarioForm(forms.ModelForm):
 class Meta: model=Scenario; fields=["organization","name","revenue_growth","cogs_percent","opex_growth","tax_percent"]
class ClientForm(forms.ModelForm):
 class Meta: model=Client; fields=["organization","name","email","phone","notes"]
class DocumentForm(forms.ModelForm):
 class Meta: model=WorkspaceDocument; fields=["organization","title","file"]
class UploadForm(forms.Form):
 organization=forms.ModelChoiceField(queryset=Organization.objects.all())
 period=forms.ModelChoiceField(queryset=FinancialPeriod.objects.all())
 file=forms.FileField()
class AskForm(forms.Form):
 question=forms.CharField(widget=forms.Textarea(attrs={"rows":3,"placeholder":"e.g. Why did EBITDA margin decline?"}))
