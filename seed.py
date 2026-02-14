from app import create_app, db
from app.models import Category, Subscription, Budget, FrequencyType, StatusType
from datetime import date, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        print("🗑️  Cleaning database...")
        db.drop_all()  
        db.create_all() 

        # --- 1. Create Budget ---
        print("💰 Setting initial budget...")
        initial_budget = Budget(monthly_limit=200.00)
        db.session.add(initial_budget)

        # --- 2. Create Categories ---
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

        # --- 3. Create Subscriptions ---
        print("💳 Creating subscriptions...")
        
        def days_ago(d):
            return date.today() - timedelta(days=d)

        subscriptions = [
            Subscription(
                name="Netflix",
                price=15.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Entertainment"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(365) # 1 year ago
            ),
            Subscription(
                name="Spotify Premium",
                price=9.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Entertainment"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(730) # 2 years ago
            ),
            Subscription(
                name="Gym Membership",
                price=45.00,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Health"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(30)
            ),
            Subscription(
                name="Amazon Prime",
                price=139.00,
                frequency=FrequencyType.YEARLY,
                category_id=categories["Shopping"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(400)
            ),
            Subscription(
                name="ChatGPT Plus",
                price=20.00,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Productivity"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(180)
            ),
            Subscription(
                name="Internet Bill",
                price=89.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Utilities"].id,
                status=StatusType.ACTIVE,
                start_date=days_ago(1000)
            ),
            Subscription(
                name="Duolingo",
                price=6.99,
                frequency=FrequencyType.MONTHLY,
                category_id=categories["Education"].id,
                status=StatusType.CANCELLED, # Cancelled item
                start_date=days_ago(60)
            )
        ]

        for sub in subscriptions:
            db.session.add(sub)
            
        db.session.commit()
        print(f"✅ Database seeded! Budget set to $200, added {len(categories)} categories and {len(subscriptions)} subscriptions.")

if __name__ == "__main__":
    seed_database()