from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=180)
    industry = models.CharField(max_length=120, blank=True)
    currency = models.CharField(max_length=8, default="INR")
    financial_year_start_month = models.PositiveSmallIntegerField(default=4)
    gstin = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class FinancialPeriod(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=80)
    start_date = models.DateField()
    end_date = models.DateField()
    is_actual = models.BooleanField(default=True)
    class Meta: ordering = ["-start_date"]
    def __str__(self): return f"{self.organization} · {self.name}"

class FinancialEntry(models.Model):
    TYPES = [("revenue","Revenue"),("cogs","Cost of goods sold"),("opex","Operating expenses"),
             ("other_income","Other income"),("interest","Interest expense"),("tax","Tax expense"),
             ("cash","Cash & equivalents"),("receivables","Trade receivables"),("inventory","Inventory"),
             ("current_assets","Other current assets"),("fixed_assets","Fixed assets"),
             ("payables","Trade payables"),("short_debt","Short-term debt"),("long_debt","Long-term debt"),
             ("equity","Equity"),("depreciation","Depreciation"),("capex","Capital expenditure")]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="entries")
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name="entries")
    category = models.CharField(max_length=30, choices=TYPES)
    label = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    department = models.CharField(max_length=100, blank=True)
    segment = models.CharField(max_length=100, blank=True)
    customer = models.CharField(max_length=150, blank=True)
    source = models.CharField(max_length=80, default="manual")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["category","label"]
    def __str__(self): return f"{self.label}: {self.amount}"

class BudgetLine(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE)
    category = models.CharField(max_length=30, choices=FinancialEntry.TYPES)
    label = models.CharField(max_length=180)
    budget_amount = models.DecimalField(max_digits=16, decimal_places=2)
    department = models.CharField(max_length=100, blank=True)

class Scenario(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    revenue_growth = models.DecimalField(max_digits=7, decimal_places=2, default=10)
    cogs_percent = models.DecimalField(max_digits=7, decimal_places=2, default=45)
    opex_growth = models.DecimalField(max_digits=7, decimal_places=2, default=8)
    tax_percent = models.DecimalField(max_digits=7, decimal_places=2, default=25)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisReport(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=180)
    report_type = models.CharField(max_length=60, default="Financial health")
    summary = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class Client(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)

class WorkspaceDocument(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="vfa_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AuditEvent(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=180)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta: ordering = ["-created_at"]
