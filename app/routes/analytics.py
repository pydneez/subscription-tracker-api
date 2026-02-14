from flask import Blueprint, jsonify, abort
from app.models import Subscription, StatusType

bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@bp.route('', methods=['GET'])
def get_analytics_dashboard():
    try:
        subs = Subscription.query.filter_by(status=StatusType.ACTIVE).all()

        total_monthly_spend = 0
        category_totals = {}
        subscriptions_breakdown = []

        for sub in subs:

            cost = sub.monthly_cost
            
            total_monthly_spend += cost

            # Category aggregation
            cat_name = sub.category_obj.name
            category_totals[cat_name] = category_totals.get(cat_name, 0) + cost

            subscriptions_breakdown.append({
                "name": sub.name,
                "monthly_cost": round(cost, 2),
                "category": cat_name
            })

        # 3. Find Top Category
        top_cat_name = max(category_totals, key=category_totals.get) if category_totals else None
        
        return jsonify({
            "financial_summary": {
                "total_monthly_cost": round(total_monthly_spend, 2),
                "total_yearly_projection": round(total_monthly_spend * 12, 2),
                "active_subscription_count": len(subs)
            },
            "category_insights": {
                "top_spending_category": top_cat_name,
                "top_category_monthly_total": round(category_totals[top_cat_name], 2) if top_cat_name else 0,
                "all_category_totals": {k: round(v, 2) for k, v in category_totals.items()}
            },
            "subscriptions": subscriptions_breakdown
        }), 200

    except Exception as e:
        abort(500, description=str(e))