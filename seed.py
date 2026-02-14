from app import create_app, db
from app.models import Category, Subscription, FrequencyType, StatusType

app = create_app()

def seed_database():
    with app.app_context():
        print("🗑️  Cleaning database...")
        db.drop_all()  
        db.create_all() 

        # --- 1. Create Categories ---
        print("📦 Creating categories...")
        categories = {
            "Entertainment": Category(name="Entertainment"),
            "Productivity": Category(name="Productivity"),
            "Utilities": Category(name="Utilities"),
            "Health": Category(name="Health & Fitness"),
            "Food": Category(name="Food & Drink"),
            "Shopping": Category(name="Shopping"),
            "Education": Category(name="Education")
        }

        for cat in categories.values():
            db.session.add(cat)
        
        db.session.commit()

        # --- 2. Create Subscriptions ---
        print("💳 Creating subscriptions...")
        subscriptions = [
            Subscription(
                name="Netflix",
                price=15.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Entertainment"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="Spotify Premium",
                price=9.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Entertainment"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="Gym Membership",
                price=45.00,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Health"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="Amazon Prime",
                price=139.00,
                frequency=FrequencyType.YEARLY,
                category_id=categories["Shopping"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="ChatGPT Plus",
                price=20.00,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Productivity"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="Internet Bill",
                price=89.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Utilities"].id,
                status=StatusType.ACTIVE
            ),
            Subscription(
                name="Duolingo",
                price=6.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Education"].id,
                status=StatusType.CANCELLED
            )
        ]

        for sub in subscriptions:
            db.session.add(sub)
            
        db.session.commit()
        print(f"✅ Database seeded! Added {len(categories)} categories and {len(subscriptions)} subscriptions.")

if __name__ == "__main__":
    seed_database()
