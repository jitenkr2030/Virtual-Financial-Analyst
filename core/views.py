import csv, io, json
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from .models import *
from .forms import *
from .calculations import summarize, financial_health, forecast, dcf
from .ai import answer_question

def org_context(request):
    org_id=request.session.get("org_id")
    org=Organization.objects.filter(id=org_id).first() if org_id else Organization.objects.first()
    if org: request.session["org_id"]=org.id
    return org

def log(request, action, detail=""):
    AuditEvent.objects.create(user=request.user if request.user.is_authenticated else None,organization=org_context(request),action=action,detail=detail)

def home(request):
    return redirect("dashboard") if request.user.is_authenticated else redirect("login")

def login_view(request):
    if request.method=="POST":
        user=authenticate(request,username=request.POST.get("username"),password=request.POST.get("password"))
        if user: login(request,user); return redirect("dashboard")
        messages.error(request,"Invalid username or password.")
    return render(request,"core/login.html")
def logout_view(request): logout(request); return redirect("login")

@login_required
def dashboard(request):
    org=org_context(request)
    if not org:
        return render(request,"core/onboarding.html",{"form":OrganizationForm()})
    periods=FinancialPeriod.objects.filter(organization=org)
    period_id=request.GET.get("period")
    period=periods.filter(id=period_id).first() if period_id else periods.first()
    s=summarize(period.entries.all()) if period else summarize([])
    score,level=financial_health(s)
    recent=AnalysisReport.objects.filter(organization=org)[:5]
    context={"org":org,"periods":periods,"period":period,"s":s,"score":score,"level":level,"recent":recent,
      "entry_count":FinancialEntry.objects.filter(organization=org).count(),"client_count":Client.objects.filter(organization=org).count()}
    return render(request,"core/dashboard.html",context)

@login_required
def organizations(request):
    return render(request,"core/organizations.html",{"items":Organization.objects.all()})
@login_required
def organization_add(request):
    form=OrganizationForm(request.POST or None)
    if form.is_valid():
        obj=form.save(); request.session["org_id"]=obj.id; log(request,"Organization created",obj.name); messages.success(request,"Organization created."); return redirect("dashboard")
    return render(request,"core/form.html",{"form":form,"title":"Add organization"})
@login_required
def periods(request):
    form=PeriodForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,"Financial period saved."); return redirect("periods")
    return render(request,"core/list_form.html",{"title":"Financial periods","form":form,"items":FinancialPeriod.objects.all()})
@login_required
def statements(request):
    org=org_context(request); entries=FinancialEntry.objects.filter(organization=org).select_related("period")
    period=request.GET.get("period")
    if period: entries=entries.filter(period_id=period)
    form=EntryForm(initial={"organization":org})
    if request.method=="POST":
        form=EntryForm(request.POST)
        if form.is_valid(): form.save(); log(request,"Financial entry added",form.cleaned_data["label"]); messages.success(request,"Entry added."); return redirect("statements")
    return render(request,"core/statements.html",{"entries":entries[:500],"form":form,"periods":FinancialPeriod.objects.filter(organization=org)})
@login_required
def sample_csv(request):
    response=HttpResponse("category,label,amount,department,segment,customer\\nrevenue,Product sales,125000,Sales,Hardware,ABC Ltd\\ncogs,Direct costs,50000,Operations,Hardware,ABC Ltd\\nopex,Office and admin,18000,Admin,,\\ncash,Cash balance,35000,Treasury,,\\nreceivables,Trade receivables,22000,Sales,,\\npayables,Trade payables,12000,Purchase,,\\nequity,Owner equity,60000,Finance,,\\n",content_type="text/csv")
    response["Content-Disposition"]='attachment; filename="vfa_sample_financial_data.csv"'
    return response
@login_required
def import_statement(request):
    form=UploadForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid():
        org=form.cleaned_data["organization"]; period=form.cleaned_data["period"]; f=form.cleaned_data["file"]
        try:
            raw=f.read()
            if f.name.lower().endswith(".xlsx"):
                import pandas as pd
                df=pd.read_excel(io.BytesIO(raw))
            else: df=__import__("pandas").read_csv(io.BytesIO(raw))
            df.columns=[str(c).strip().lower() for c in df.columns]
            required={"category","label","amount"}
            if not required.issubset(set(df.columns)): raise ValueError("Required columns: category, label, amount.")
            allowed={x[0] for x in FinancialEntry.TYPES}; count=0
            for _,row in df.iterrows():
                cat=str(row["category"]).strip().lower()
                if cat not in allowed: continue
                FinancialEntry.objects.create(organization=org,period=period,category=cat,label=str(row["label"])[:180],
                  amount=Decimal(str(row["amount"] or 0)),department=str(row.get("department",""))[:100],
                  segment=str(row.get("segment",""))[:100],customer=str(row.get("customer",""))[:150],source="import")
                count+=1
            log(request,"Financial data imported",f"{count} rows from {f.name}")
            messages.success(request,f"Imported {count} rows."); return redirect("statements")
        except Exception as e: messages.error(request,f"Import failed: {e}")
    return render(request,"core/form.html",{"form":form,"title":"Import financial data"})
@login_required
def ratios(request):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).filter(id=request.GET.get("period")).first() if request.GET.get("period") else FinancialPeriod.objects.filter(organization=org).first()
    s=summarize(period.entries.all()) if period else summarize([])
    return render(request,"core/ratios.html",{"s":s,"period":period,"periods":FinancialPeriod.objects.filter(organization=org)})
@login_required
def calculators(request):
    result=None; kind=request.POST.get("kind","")
    if request.method=="POST":
        try:
            p=lambda k: float(request.POST.get(k) or 0)
            if kind=="margin":
                result={"Gross margin %":(p("revenue")-p("cogs"))/p("revenue")*100 if p("revenue") else 0,"Contribution":p("revenue")-p("variable_cost")}
            elif kind=="break_even":
                contribution=p("price")-p("variable_cost"); result={"Break-even units":p("fixed_cost")/contribution if contribution>0 else 0,"Margin of safety units":p("units")-(p("fixed_cost")/contribution if contribution>0 else 0)}
            elif kind=="roi": result={"ROI %":(p("gain")-p("cost"))/p("cost")*100 if p("cost") else 0,"Payback period (years)":p("cost")/p("annual_cash") if p("annual_cash") else 0}
            elif kind=="npv":
                rate=p("rate")/100; vals=[float(x.strip()) for x in request.POST.get("cashflows","0,0,0").split(",")]
                result={"NPV":sum(v/((1+rate)**i) for i,v in enumerate(vals))}
            elif kind=="runway": result={"Cash runway (months)":p("cash")/p("burn") if p("burn") else 0,"Monthly burn":p("burn")}
            elif kind=="cagr":
                n=p("years"); result={"CAGR %":((p("ending")/p("beginning"))**(1/n)-1)*100 if n and p("beginning")>0 and p("ending")>=0 else 0}
        except Exception as e: result={"Error":str(e)}
    return render(request,"core/calculators.html",{"result":result,"kind":kind})
@login_required
def models_view(request):
    org=org_context(request); form=ScenarioForm(request.POST or None,initial={"organization":org})
    scenario=None; rows=[]
    if request.method=="POST" and form.is_valid():
        scenario=form.save(); log(request,"Forecast scenario created",scenario.name)
    period=FinancialPeriod.objects.filter(organization=org).first()
    if period:
        s=summarize(period.entries.all())
        selected=Scenario.objects.filter(organization=org).order_by("-id").first()
        if selected: rows=forecast(s,3,selected.revenue_growth,selected.cogs_percent,selected.opex_growth,selected.tax_percent)
    return render(request,"core/models.html",{"form":form,"scenarios":Scenario.objects.filter(organization=org),"rows":rows})
@login_required
def valuation(request):
    result=None
    if request.method=="POST":
        try:
            flows=[float(x.strip()) for x in request.POST.get("fcf","100,120,140,160,180").split(",")]
            result=dcf(flows,float(request.POST.get("wacc",12)),float(request.POST.get("growth",3)))
            result["equity_value"]=result["enterprise_value"]-float(request.POST.get("debt",0))+float(request.POST.get("cash",0))
        except Exception as e: messages.error(request,str(e))
    return render(request,"core/valuation.html",{"result":result})
@login_required
def budgets(request):
    org=org_context(request); form=BudgetForm(request.POST or None,initial={"organization":org})
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Budget line saved."); return redirect("budgets")
    lines=BudgetLine.objects.filter(organization=org).select_related("period")
    actuals={}
    for line in lines:
        actual=float(FinancialEntry.objects.filter(period=line.period,category=line.category,label=line.label).aggregate(x=Sum("amount"))["x"] or 0)
        actuals[line.id]=actual
    return render(request,"core/budgets.html",{"form":form,"lines":lines,"actuals":actuals})
@login_required
def cashflow(request):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).first(); s=summarize(period.entries.all()) if period else summarize([])
    operating=s["pat"]+s["items"].get("depreciation",0)
    fcf=operating-s["items"].get("capex",0)
    return render(request,"core/cashflow.html",{"s":s,"operating":operating,"fcf":fcf,"period":period})
@login_required
def profitability(request):
    org=org_context(request); qs=FinancialEntry.objects.filter(organization=org,category__in=["revenue","cogs","opex"])
    groups={}
    for e in qs:
        key=e.segment or e.customer or e.department or "Unclassified"
        groups.setdefault(key,{"revenue":0,"cost":0})
        if e.category=="revenue": groups[key]["revenue"]+=float(e.amount)
        else: groups[key]["cost"]+=float(e.amount)
    data=[{"name":k,"revenue":v["revenue"],"cost":v["cost"],"profit":v["revenue"]-v["cost"]} for k,v in groups.items()]
    return render(request,"core/profitability.html",{"data":data})
@login_required
def investments(request):
    result=None
    if request.method=="POST":
        try:
            cost=float(request.POST.get("cost",0)); cash=[float(x) for x in request.POST.get("flows","100,120,140").split(",")]; rate=float(request.POST.get("rate",12))/100
            npv=-cost+sum(v/(1+rate)**i for i,v in enumerate(cash,1))
            result={"NPV":npv,"Initial investment":cost,"Total inflows":sum(cash),"ROI %":((sum(cash)-cost)/cost*100 if cost else 0)}
        except Exception as e: messages.error(request,str(e))
    return render(request,"core/investments.html",{"result":result})
@login_required
def risks(request):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).first(); s=summarize(period.entries.all()) if period else summarize([])
    alerts=[]
    if s["ratios"]["Current ratio"]<1: alerts.append("Current ratio is below 1.0; short-term liquidity may be constrained.")
    if s["ratios"]["Debt / equity"]>2: alerts.append("Debt/equity exceeds 2.0x; review leverage and repayment capacity.")
    if s["ratios"]["Interest coverage"]<1.5: alerts.append("Interest coverage is below 1.5x; debt servicing headroom may be limited.")
    if s["revenue"] and s["ebitda"]<0: alerts.append("EBITDA is negative; investigate pricing, gross margin and operating cost base.")
    if not alerts: alerts.append("No threshold-based alerts from the available data. This is not a comprehensive risk assessment.")
    return render(request,"core/risks.html",{"s":s,"alerts":alerts})
@login_required
def kpis(request):
    org=org_context(request); periods=list(FinancialPeriod.objects.filter(organization=org).order_by("start_date"))
    data=[]
    for p in periods:
        s=summarize(p.entries.all()); data.append({"period":p.name,"revenue":s["revenue"],"ebitda":s["ebitda"],"pat":s["pat"]})
    return render(request,"core/kpis.html",{"data":data})
@login_required
def research(request):
    org=org_context(request)
    if request.method=="POST":
        title=request.POST.get("title","Research note"); body=request.POST.get("body","")
        AnalysisReport.objects.create(organization=org,title=title,report_type="Research note",summary=body,created_by=request.user)
        messages.success(request,"Research note saved.")
    return render(request,"core/research.html",{"reports":AnalysisReport.objects.filter(organization=org,report_type="Research note")})
@login_required
def reports(request):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).first(); s=summarize(period.entries.all()) if period else summarize([])
    if request.method=="POST":
        title=request.POST.get("title","Financial analysis report")
        score,level=financial_health(s)
        summary=f"Period: {period.name if period else 'No period'} | Revenue: {s['revenue']:,.2f} | EBITDA: {s['ebitda']:,.2f} | PAT: {s['pat']:,.2f} | Health: {score}/100 ({level})"
        AnalysisReport.objects.create(organization=org,title=title,summary=summary,created_by=request.user)
        messages.success(request,"Report generated and saved.")
    return render(request,"core/reports.html",{"reports":AnalysisReport.objects.filter(organization=org),"s":s,"period":period})
@login_required
def export_report(request,kind):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).first(); s=summarize(period.entries.all()) if period else summarize([])
    if kind=="csv":
        out=io.StringIO(); w=csv.writer(out); w.writerow(["Metric","Value"])
        for k in ["revenue","cogs","gross_profit","opex","ebitda","ebit","pat"]: w.writerow([k,s[k]])
        for k,v in s["ratios"].items(): w.writerow([k,v])
        resp=HttpResponse(out.getvalue(),content_type="text/csv"); resp["Content-Disposition"]='attachment; filename="vfa_financial_report.csv"'; return resp
    if kind=="xlsx":
        import pandas as pd
        rows=[{"Metric":k,"Value":v} for k,v in s.items() if isinstance(v,(int,float))]
        rows += [{"Metric":k,"Value":v} for k,v in s["ratios"].items()]
        b=io.BytesIO(); pd.DataFrame(rows).to_excel(b,index=False)
        resp=HttpResponse(b.getvalue(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"); resp["Content-Disposition"]='attachment; filename="vfa_financial_report.xlsx"'; return resp
    if kind=="pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        b=io.BytesIO(); c=canvas.Canvas(b,pagesize=A4); y=800
        c.setFont("Helvetica-Bold",18); c.drawString(50,y,"Virtual Financial Analyst"); y-=35
        c.setFont("Helvetica",11)
        for k in ["revenue","cogs","gross_profit","opex","ebitda","ebit","pat"]:
            c.drawString(50,y,f"{k.replace('_',' ').title()}: {s[k]:,.2f}"); y-=20
        y-=10
        for k,v in s["ratios"].items(): c.drawString(50,y,f"{k}: {v:,.2f}"); y-=18
        c.save(); resp=HttpResponse(b.getvalue(),content_type="application/pdf"); resp["Content-Disposition"]='attachment; filename="vfa_financial_report.pdf"'; return resp
    return redirect("reports")
@login_required
def assistant(request):
    org=org_context(request); period=FinancialPeriod.objects.filter(organization=org).first(); s=summarize(period.entries.all()) if period else summarize([])
    answer=None; form=AskForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        answer=answer_question(form.cleaned_data["question"],s); log(request,"AI assistant query",form.cleaned_data["question"])
    return render(request,"core/assistant.html",{"form":form,"answer":answer,"s":s})
@login_required
def clients(request):
    org=org_context(request); form=ClientForm(request.POST or None,initial={"organization":org})
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Client saved."); return redirect("clients")
    return render(request,"core/clients.html",{"form":form,"items":Client.objects.filter(organization=org)})
@login_required
def documents(request):
    org=org_context(request); form=DocumentForm(request.POST or None,request.FILES or None,initial={"organization":org})
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Document uploaded."); return redirect("documents")
    return render(request,"core/documents.html",{"form":form,"items":WorkspaceDocument.objects.filter(organization=org)})
@login_required
def audit_log(request):
    return render(request,"core/audit.html",{"items":AuditEvent.objects.all()[:200]})
