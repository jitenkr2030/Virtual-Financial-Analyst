# Generated for the VFA starter application.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Organization", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=180)), ("industry", models.CharField(blank=True,max_length=120)),
            ("currency", models.CharField(default="INR",max_length=8)), ("financial_year_start_month",models.PositiveSmallIntegerField(default=4)),
            ("gstin",models.CharField(blank=True,max_length=20)),("created_at",models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name="Client",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=180)),("email",models.EmailField(blank=True,max_length=254)),
            ("phone",models.CharField(blank=True,max_length=40)),("notes",models.TextField(blank=True)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.organization"))]),
        migrations.CreateModel(name="FinancialPeriod",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=80)),("start_date",models.DateField()),("end_date",models.DateField()),
            ("is_actual",models.BooleanField(default=True)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="periods",to="core.organization"))],
            options={"ordering":["-start_date"]}),
        migrations.CreateModel(name="FinancialEntry",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("category",models.CharField(choices=[("revenue","Revenue"),("cogs","Cost of goods sold"),("opex","Operating expenses"),("other_income","Other income"),("interest","Interest expense"),("tax","Tax expense"),("cash","Cash & equivalents"),("receivables","Trade receivables"),("inventory","Inventory"),("current_assets","Other current assets"),("fixed_assets","Fixed assets"),("payables","Trade payables"),("short_debt","Short-term debt"),("long_debt","Long-term debt"),("equity","Equity"),("depreciation","Depreciation"),("capex","Capital expenditure")],max_length=30)),
            ("label",models.CharField(max_length=180)),("amount",models.DecimalField(decimal_places=2,max_digits=16)),
            ("department",models.CharField(blank=True,max_length=100)),("segment",models.CharField(blank=True,max_length=100)),
            ("customer",models.CharField(blank=True,max_length=150)),("source",models.CharField(default="manual",max_length=80)),
            ("created_at",models.DateTimeField(auto_now_add=True)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="entries",to="core.organization")),
            ("period",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="entries",to="core.financialperiod"))],
            options={"ordering":["category","label"]}),
        migrations.CreateModel(name="BudgetLine",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("category",models.CharField(choices=[("revenue","Revenue"),("cogs","Cost of goods sold"),("opex","Operating expenses"),("other_income","Other income"),("interest","Interest expense"),("tax","Tax expense"),("cash","Cash & equivalents"),("receivables","Trade receivables"),("inventory","Inventory"),("current_assets","Other current assets"),("fixed_assets","Fixed assets"),("payables","Trade payables"),("short_debt","Short-term debt"),("long_debt","Long-term debt"),("equity","Equity"),("depreciation","Depreciation"),("capex","Capital expenditure")],max_length=30)),
            ("label",models.CharField(max_length=180)),("budget_amount",models.DecimalField(decimal_places=2,max_digits=16)),
            ("department",models.CharField(blank=True,max_length=100)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.organization")),
            ("period",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.financialperiod"))]),
        migrations.CreateModel(name="Scenario",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=100)),("revenue_growth",models.DecimalField(decimal_places=2,default=10,max_digits=7)),
            ("cogs_percent",models.DecimalField(decimal_places=2,default=45,max_digits=7)),("opex_growth",models.DecimalField(decimal_places=2,default=8,max_digits=7)),
            ("tax_percent",models.DecimalField(decimal_places=2,default=25,max_digits=7)),("created_at",models.DateTimeField(auto_now_add=True)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.organization"))]),
        migrations.CreateModel(name="AnalysisReport",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("title",models.CharField(max_length=180)),("report_type",models.CharField(default="Financial health",max_length=60)),
            ("summary",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),
            ("created_by",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.organization"))]),
        migrations.CreateModel(name="WorkspaceDocument",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("title",models.CharField(max_length=180)),("file",models.FileField(upload_to="vfa_documents/")),
            ("uploaded_at",models.DateTimeField(auto_now_add=True)),
            ("organization",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to="core.organization"))]),
        migrations.CreateModel(name="AuditEvent",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("action",models.CharField(max_length=180)),("detail",models.TextField(blank=True)),
            ("created_at",models.DateTimeField(default=django.utils.timezone.now)),
            ("organization",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to="core.organization")),
            ("user",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL))],
            options={"ordering":["-created_at"]}),
    ]
