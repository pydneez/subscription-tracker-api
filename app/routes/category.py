from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Category

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_json() for c in cats]), 200

@bp.route('', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description='Missing required field: name')
    
    # Check if unique
    if Category.query.filter_by(name=data['name']).first():
         abort(409, description=f"Category '{data['name']}' already exists")

    new_cat = Category(name=data['name'])
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category': new_cat.to_json()}), 201