from django.contrib import admin
from .models import *
admin.site.register([Organization, FinancialPeriod, FinancialEntry, BudgetLine, Scenario, AnalysisReport, Client, WorkspaceDocument, AuditEvent])
