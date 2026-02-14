from flask import Blueprint, jsonify, request, abort
from app import db
from app.models import Budget, Subscription, StatusType

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('', methods=['GET'])
def get_budget_status():
    """Returns budget settings AND current health status."""
    try:
        budget = Budget.query.first()
        if not budget:
            return jsonify({"message": "Budget not set", "monthly_limit": 0}), 200

        # Calculate current spending using Model Logic
        subs = Subscription.query.filter_by(status=StatusType.ACTIVE).all()
        current_spend = sum(s.monthly_cost for s in subs)
        
        remaining = budget.monthly_limit - current_spend
        usage_percent = (current_spend / budget.monthly_limit) * 100 if budget.monthly_limit > 0 else 0

        # Determine Health Label
        status_label = "Good"
        if usage_percent > 100: status_label = "Over Budget"
        elif usage_percent > 85: status_label = "Warning"

        return jsonify({
            "config": {
                "monthly_limit": budget.monthly_limit
            },
            "status": {
                "current_spend": round(current_spend, 2),
                "remaining": round(remaining, 2),
                "usage_percent": round(usage_percent, 1),
                "health_label": status_label
            }
        }), 200
    except Exception as e:
        abort(500, description=str(e))

@bp.route('', methods=['PUT'])
def update_budget():
    data = request.get_json()
    if not data or 'limit' not in data:
        abort(400, description="Missing required field: limit")

    try:
        limit = float(data['limit'])
        if limit <= 0: abort(400, description="Budget must be positive")
    except ValueError:
        abort(400, description="Limit must be a number")

    budget = Budget.query.first()
    if not budget:
        budget = Budget(monthly_limit=limit)
        db.session.add(budget)
    else:
        budget.monthly_limit = limit

    db.session.commit()
    return jsonify({"message": "Budget updated", "monthly_limit": budget.monthly_limit}), 200