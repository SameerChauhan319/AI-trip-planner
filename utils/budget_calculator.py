from typing import Dict, Any

# Supported currencies: symbol, name, INR conversion rate (approx)
CURRENCY_OPTIONS = {
    "INR — Indian Rupee (₹)":       {"symbol": "₹",  "code": "INR",  "rate": 1.0},
    "USD — US Dollar ($)":           {"symbol": "$",  "code": "USD",  "rate": 0.012},
    "EUR — Euro (€)":                {"symbol": "€",  "code": "EUR",  "rate": 0.011},
    "GBP — British Pound (£)":       {"symbol": "£",  "code": "GBP",  "rate": 0.0095},
    "AED — UAE Dirham (د.إ)":        {"symbol": "د.إ","code": "AED",  "rate": 0.044},
    "SGD — Singapore Dollar (S$)":   {"symbol": "S$", "code": "SGD",  "rate": 0.016},
    "THB — Thai Baht (฿)":           {"symbol": "฿",  "code": "THB",  "rate": 0.42},
    "JPY — Japanese Yen (¥)":        {"symbol": "¥",  "code": "JPY",  "rate": 1.82},
    "AUD — Australian Dollar (A$)":  {"symbol": "A$", "code": "AUD",  "rate": 0.018},
    "CAD — Canadian Dollar (C$)":    {"symbol": "C$", "code": "CAD",  "rate": 0.016},
}

def get_budget_tier(total_budget: float, days: int) -> str:
    """Classifies the budget into a tier (Budget, Mid-Range, Luxury) based on daily spending."""
    daily_budget = total_budget / max(1, days)
    if daily_budget < 3000:
        return "Budget"
    elif daily_budget <= 8000:
        return "Mid-Range"
    else:
        return "Luxury"

def estimate_expenses(total_budget: float, days: int) -> Dict[str, int]:
    """
    Estimates realistic trip expenses per category based on total budget and duration.
    """
    tier = get_budget_tier(total_budget, days)

    if tier == "Budget":
        allocations = {
            "hotel": 0.28, "food": 0.25, "transportation": 0.22,
            "attractions_activities": 0.13, "shopping_misc": 0.12
        }
    elif tier == "Mid-Range":
        allocations = {
            "hotel": 0.35, "food": 0.24, "transportation": 0.18,
            "attractions_activities": 0.13, "shopping_misc": 0.10
        }
    else:  # Luxury
        allocations = {
            "hotel": 0.42, "food": 0.20, "transportation": 0.15,
            "attractions_activities": 0.13, "shopping_misc": 0.10
        }

    estimated_breakdown = {}
    running_total = 0

    for category, pct in list(allocations.items())[:-1]:
        cost = round((total_budget * pct) / 100) * 100
        estimated_breakdown[category] = int(cost)
        running_total += cost

    last_cat = list(allocations.keys())[-1]
    estimated_breakdown[last_cat] = int(total_budget - running_total)

    return estimated_breakdown


def format_currency(amount: float, symbol: str = "₹", code: str = "INR") -> str:
    """
    Formats a numeric amount into a currency string using the given symbol & code.
    Uses Indian comma formatting for INR, no decimals for JPY, 2 decimals for others.
    """
    try:
        val = float(amount)
        if code == "INR":
            s = str(int(val))
            if len(s) <= 3:
                return f"₹{s}"
            last_three = s[-3:]
            remaining = s[:-3]
            out = []
            while len(remaining) > 2:
                out.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                out.insert(0, remaining)
            return f"₹{','.join(out)},{last_three}"
        elif code == "JPY":
            return f"{symbol}{int(val):,}"
        else:
            return f"{symbol}{val:,.2f}"
    except Exception:
        return f"{symbol}{amount:,.2f}"


def format_inr(amount: float) -> str:
    """Backward-compatible alias — formats amount as Indian Rupee (₹)."""
    return format_currency(amount, symbol="₹", code="INR")


def validate_expenses(breakdown: Dict[str, int], total_limit: float) -> bool:
    """Verifies if the sum of category expenses is within the total trip budget limit."""
    return sum(breakdown.values()) <= total_limit


if __name__ == "__main__":
    print("Testing Budget Calculator...")
    b = 20000
    d = 4
    print(f"Budget: {format_inr(b)} for {d} days ({get_budget_tier(b, d)} tier)")
    est = estimate_expenses(b, d)
    for k, v in est.items():
        print(f" - {k.replace('_', ' ').capitalize()}: {format_inr(v)}")
    print(f"Total: {format_inr(sum(est.values()))} (Valid: {validate_expenses(est, b)})")
