def answer_question(question, summary):
    """Explainable local assistant. Optional LLM integration can be added without changing core calculations."""
    q=question.lower(); r=summary.get("ratios",{})
    if any(x in q for x in ["cash","liquidity","working capital"]):
        return (f"Working capital is {summary['ratios']['Working capital']:,.2f}. "
                f"Current ratio is {r.get('Current ratio',0):.2f}x and quick ratio is {r.get('Quick ratio',0):.2f}x. "
                "Review receivable collection, inventory ageing and short-term obligations. This is a rule-based explanation, not an audit opinion.")
    if any(x in q for x in ["margin","profit","ebitda"]):
        return (f"Revenue is {summary['revenue']:,.2f}; gross profit is {summary['gross_profit']:,.2f}; "
                f"EBITDA is {summary['ebitda']:,.2f}; PAT is {summary['pat']:,.2f}. "
                f"EBITDA margin is {r.get('EBITDA margin',0):.2f}%. Compare product/customer mix, pricing, COGS and operating costs.")
    if any(x in q for x in ["debt","solvency","risk"]):
        return (f"Debt/equity is {r.get('Debt / equity',0):.2f}x and interest coverage is {r.get('Interest coverage',0):.2f}x. "
                "Check repayment schedules, covenant headroom, refinancing exposure and downside cash-flow scenarios.")
    return ("Based on the selected financial period: "
      f"revenue {summary['revenue']:,.2f}, EBITDA {summary['ebitda']:,.2f}, PAT {summary['pat']:,.2f}. "
      "Start by reviewing trend, budget variance, working capital and debt service. Ask a focused question about one of these areas for a more specific explanation.")
