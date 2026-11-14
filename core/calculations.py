from decimal import Decimal
from math import isfinite

def safe_div(a,b):
    try: return float(a)/float(b) if float(b) else 0.0
    except (TypeError,ValueError,ZeroDivisionError): return 0.0

def summarize(entries):
    d = {}
    for e in entries: d[e.category] = d.get(e.category,0.0)+float(e.amount)
    revenue=d.get("revenue",0); cogs=d.get("cogs",0); opex=d.get("opex",0)
    other=d.get("other_income",0); interest=d.get("interest",0); tax=d.get("tax",0)
    gross=revenue-cogs; ebitda=gross-opex; ebit=ebitda-d.get("depreciation",0)
    pat=ebit+other-interest-tax
    current_assets=d.get("cash",0)+d.get("receivables",0)+d.get("inventory",0)+d.get("current_assets",0)
    current_liab=d.get("payables",0)+d.get("short_debt",0)
    total_assets=current_assets+d.get("fixed_assets",0)
    debt=d.get("short_debt",0)+d.get("long_debt",0)
    equity=d.get("equity",0)
    ratios={
      "Gross margin":safe_div(gross,revenue)*100, "EBITDA margin":safe_div(ebitda,revenue)*100,
      "Net profit margin":safe_div(pat,revenue)*100, "Current ratio":safe_div(current_assets,current_liab),
      "Quick ratio":safe_div(current_assets-d.get("inventory",0),current_liab),
      "Debt / equity":safe_div(debt,equity), "ROA":safe_div(pat,total_assets)*100,
      "ROE":safe_div(pat,equity)*100, "Working capital":current_assets-current_liab,
      "Interest coverage":safe_div(ebit,interest),
    }
    return {"items":d,"revenue":revenue,"cogs":cogs,"gross_profit":gross,"opex":opex,
      "ebitda":ebitda,"ebit":ebit,"pat":pat,"current_assets":current_assets,
      "current_liabilities":current_liab,"total_assets":total_assets,"debt":debt,"equity":equity,
      "ratios":ratios}

def financial_health(s):
    r=s["ratios"]; score=50
    score += min(max(r["Gross margin"],0),60)*.25
    score += min(max(r["EBITDA margin"],-20),30)*.55
    score += min(r["Current ratio"],3)*5
    score -= min(r["Debt / equity"],5)*3
    score=max(0,min(100,round(score)))
    level="Strong" if score>=75 else "Stable" if score>=55 else "Needs attention"
    return score,level

def forecast(s, years=3, revenue_growth=10, cogs_pct=None, opex_growth=8, tax_pct=25):
    revenue=s["revenue"]; cogs_pct=(safe_div(s["cogs"],revenue)*100 if cogs_pct is None else float(cogs_pct))
    opex=s["opex"]; rows=[]
    for y in range(1,years+1):
        revenue*=1+float(revenue_growth)/100
        cogs=revenue*cogs_pct/100; opex*=1+float(opex_growth)/100
        ebitda=revenue-cogs-opex; tax=max(0,ebitda*float(tax_pct)/100)
        rows.append({"year":f"Year {y}","revenue":revenue,"cogs":cogs,"opex":opex,"ebitda":ebitda,"tax":tax,"pat":ebitda-tax})
    return rows

def dcf(fcf_values, wacc, terminal_growth):
    wacc=float(wacc)/100; g=float(terminal_growth)/100
    if wacc <= g: raise ValueError("WACC must be greater than terminal growth.")
    pv=sum(float(v)/((1+wacc)**i) for i,v in enumerate(fcf_values,1))
    terminal=float(fcf_values[-1])*(1+g)/(wacc-g) if fcf_values else 0
    return {"pv_cash_flows":pv,"terminal_value":terminal,"pv_terminal":terminal/((1+wacc)**len(fcf_values)) if fcf_values else 0,
            "enterprise_value":pv+(terminal/((1+wacc)**len(fcf_values)) if fcf_values else 0)}
