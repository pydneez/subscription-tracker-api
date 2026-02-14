from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Subscription, Category, FrequencyType, StatusType, Budget
from sqlalchemy import func
from datetime import date, datetime

bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

# --- Helper ---
def get_or_create_category(category_name):
    category = Category.query.filter(func.lower(Category.name) == category_name.lower()).first()
    if not category:
        category = Category(name=category_name.capitalize())
        db.session.add(category)
        db.session.commit() 
    return category

# --- Routes ---

# GET ALL (with optional ?category= and ?status= filters)
@bp.route('', methods=['GET'])
def get_subscriptions():
    query = Subscription.query

    # get param
    category_name = request.args.get('category')
    status_name = request.args.get('status')

    # filter for category
    if category_name:
        query = query.join(Category).filter(
            func.lower(Category.name) == category_name.lower()
        )

    # filter for status (chain filter from above)
    if status_name:
        query = query.filter(
            func.lower(Subscription.status) == status_name.lower()
        )

    subs = query.all()
    if not subs:
             return jsonify({
                'message': f'No subscriptions found in category: {category_name}', 
                'subscriptions': []
            }), 404

    # return result
    return jsonify([sub.to_json() for sub in subs]), 200
@bp.route('/<int:id>', methods=['GET'])
def get_subscription(id):
    sub = db.session.get(Subscription, id)
    if not sub: abort(404, description=f"Subscription {id} not found")
    return jsonify(sub.to_json()), 200

@bp.route('', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()

        # 1. Validate required fields
        required = {'name', 'price', 'frequency', 'category'} 
        if not data or not all(k in data for k in required):
            abort(400, description=f"Missing required fields: {', '.join(required - data.keys())}")

        # Check Duplicates
        if Subscription.query.filter(func.lower(Subscription.name) == data['name'].lower()).first():
            abort(409, description=f"Subscription '{data['name']}' already exists.")

        # Data Conversion
        try:
            price = float(data['price'])
            if price < 0: raise ValueError
            freq_enum = FrequencyType(data['frequency'])
        except ValueError:
            abort(400, description="Invalid price or frequency")

        status_enum = StatusType.ACTIVE
        if 'status' in data:
            try: status_enum = StatusType(data['status'])
            except ValueError: abort(400, description="Invalid status")

        start_date = date.today()
        if 'start_date' in data:
            try: start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError: abort(400, description="Invalid date format YYYY-MM-DD")

        # Create
        cat_obj = get_or_create_category(data['category'])
        new_sub = Subscription(
            name=data['name'], price=price, frequency=freq_enum,
            category_id=cat_obj.id, status=status_enum, start_date=start_date
        )
        db.session.add(new_sub)
        db.session.commit()
        
        return jsonify({'message': 'Created', 'subscription': new_sub.to_json()}), 201
        
    except Exception as e:
        if hasattr(e, 'code'): raise e
        abort(500, description=str(e))

# UPDATE
@bp.route('/<int:id>', methods=['PUT'])
def update_subscription(id):
    try:
        sub = db.session.get(Subscription, id)
        if not sub:
             abort(404, description=f"Subscription with ID {id} not found")

        data = request.get_json()

        if 'name' in data: sub.name = data['name']
        
        if 'price' in data:
            try:
                val = float(data['price'])
                if val < 0: raise ValueError
                sub.price = val
            except ValueError:
                abort(400, description='Invalid price')

        if 'frequency' in data:
            try:
                sub.frequency = FrequencyType(data['frequency'])
            except ValueError:
                abort(400, description=f'Invalid frequency. Allowed: {[e.value for e in FrequencyType]}')
        
        if 'status' in data:
            try:
                sub.status = StatusType(data['status'])
            except ValueError:
                abort(400, description=f'Invalid status. Allowed: {[e.value for e in StatusType]}')

        if 'category' in data: 
            cat_obj = get_or_create_category(data['category'])
            sub.category_id = cat_obj.id

        db.session.commit()
        return jsonify({'message': 'Updated', 'subscription': sub.to_json()}), 200
    except Exception as e:
        if hasattr(e, 'code'): raise e
        abort(500, description=str(e))

# DELETE
@bp.route('/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    sub = db.session.get(Subscription, id)
    if not sub:
        abort(404, description=f"Cannot delete: Subscription {id} does not exist")
    
    deleted_data = sub.to_json()
    db.session.delete(sub)
    db.session.commit()

    return jsonify({
        'message': 'Deleted successfully', 
        'subscription': deleted_data
    }), 200