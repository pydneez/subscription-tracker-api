from . import db
import enum
from datetime import date

class FrequencyType(enum.Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class StatusType(enum.Enum):
    ACTIVE = "Active"
    PAUSED = "Paused"
    CANCELLED = "Cancelled"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    subscriptions = db.relationship('Subscription', backref='category_obj', lazy=True)

    def to_json(self):
        return {"id": self.id, "name": self.name}

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, nullable=False, default=0.0)

    def to_json(self):
        return {"id": self.id, "monthly_limit": self.monthly_limit}

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.Enum(FrequencyType), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum(StatusType), nullable=False, default=StatusType.ACTIVE)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    @property
    def monthly_cost(self):

        if self.frequency == FrequencyType.WEEKLY:
            return self.price * 4
        elif self.frequency == FrequencyType.YEARLY:
            return self.price / 12
        return self.price

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "frequency": self.frequency.value,
            "category": self.category_obj.name if self.category_obj else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "status": self.status.value,
            "monthly_cost": round(self.monthly_cost, 2)
        }