import unittest
import json
from app import create_app, db
from app.models import Subscription, Category, Budget, FrequencyType, StatusType
from datetime import date

class SubscriptionTrackerTestCase(unittest.TestCase):
    
    def setUp(self):
        """Run before every test: Setup in-memory DB."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Run after every test: Clean up and dispose DB connection."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    # =================================================================
    # 1. CATEGORY TESTS
    # =================================================================

    def test_category_creation_happy_path(self):
        """Verify that a valid category is created successfully (201)."""
        res = self.client.post('/categories', json={"name": "Gaming"})
        self.assertEqual(res.status_code, 201)
        self.assertIn("Gaming", str(res.data))

    def test_category_creation_duplicate_fails(self):
        """Verify that creating a duplicate category returns an error."""
        # Create 'Music' once
        self.client.post('/categories', json={"name": "Music"})
        # Try to create it again
        res = self.client.post('/categories', json={"name": "Music"})
        
        # Expecting 409 Conflict
        self.assertEqual(res.status_code, 409) 

    # =================================================================
    # 2. BUDGET TESTS
    # =================================================================

    def test_budget_lifecycle_update_and_retrieve(self):
        """Verify we can set a budget limit and retrieve the same value."""
        # 1. Set Budget
        res = self.client.put('/budgets', json={"limit": 500.00})
        self.assertEqual(res.status_code, 200)
        
        # 2. Get Budget
        res_get = self.client.get('/budgets')
        data = json.loads(res_get.data)
        self.assertEqual(data['config']['monthly_limit'], 500.00)
        self.assertEqual(data['status']['health_label'], "Good")

    # =================================================================
    # 3. SUBSCRIPTION TESTS - CREATION & VALIDATION
    # =================================================================

    def test_subscription_creation_valid_payload(self):
        """Verify that a perfectly valid subscription is created (201)."""
        payload = {
            "name": "Hulu", 
            "price": 10, 
            "frequency": "Monthly", 
            "category": "TV", 
            "start_date": "2023-01-01"
        }
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['subscription']['name'], "Hulu")

    def test_subscription_creation_duplicate_name_fails(self):
        """Verify that creating a subscription with an existing name returns 409 Conflict."""
        payload = {"name": "Hulu", "price": 10, "frequency": "Monthly", "category": "TV"}
        self.client.post('/subscriptions', json=payload)
        
        # Try creating again
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 409) 
        self.assertIn("already exists", str(res.data))
    
    def test_subscription_validation_rejects_negative_price(self):
        """Verify that a negative price returns 400 Bad Request."""
        res = self.client.post('/subscriptions', json={
            "name": "Negative Price", 
            "price": -10.00, 
            "frequency": "Monthly", 
            "category": "Test"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid price", str(res.data))

    def test_subscription_validation_rejects_invalid_date_format(self):
        """Verify that a non-YYYY-MM-DD date string returns 400 Bad Request."""
        res = self.client.post('/subscriptions', json={
            "name": "Bad Date", 
            "price": 10.00, 
            "frequency": "Monthly", 
            "category": "Test",
            "start_date": "not-a-date"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid date format", str(res.data))

    def test_subscription_validation_rejects_missing_fields(self):
        """Verify that missing required fields (frequency) returns 400 Bad Request."""
        res = self.client.post('/subscriptions', json={
            "name": "Missing Field", 
            "price": 10.00, 
            "category": "Test"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("frequency", str(res.data))

    # =================================================================
    # 4. SUBSCRIPTION TESTS - RETRIEVAL & DELETION
    # =================================================================

    def test_get_subscriptions_filtering_by_status_and_category(self):
        """Verify filtering logic works for Category only, Status only, and Both combined."""
        # 1. Setup Data
        self.client.post('/subscriptions', json={"name": "Netflix", "price": 10, "frequency": "Monthly", "category": "Entertainment", "status": "Active"})
        self.client.post('/subscriptions', json={"name": "Hulu", "price": 10, "frequency": "Monthly", "category": "Entertainment", "status": "Cancelled"})
        self.client.post('/subscriptions', json={"name": "Zoom", "price": 15, "frequency": "Monthly", "category": "Work", "status": "Active"})

        # 2. Test Filter by STATUS only (?status=Active)
        res_status = self.client.get('/subscriptions?status=Active')
        data_status = json.loads(res_status.data)
        self.assertEqual(len(data_status), 2) # Netflix, Zoom

        # 3. Test Filter by CATEGORY only (?category=Entertainment)
        res_cat = self.client.get('/subscriptions?category=Entertainment')
        data_cat = json.loads(res_cat.data)
        self.assertEqual(len(data_cat), 2) # Netflix, Hulu

        # 4. Test COMBINED Filter (?category=Entertainment&status=Active)
        res_both = self.client.get('/subscriptions?category=Entertainment&status=Active')
        data_both = json.loads(res_both.data)
        self.assertEqual(len(data_both), 1) # Only Netflix

    def test_delete_subscription_removes_data(self):
        """Verify that deleting a subscription removes it from the database."""
        # Create
        self.client.post('/subscriptions', json={"name": "Del", "price": 10, "frequency": "Monthly", "category": "Test"})
        
        # Delete (ID is 1 because DB is fresh)
        res = self.client.delete('/subscriptions/1')
        self.assertEqual(res.status_code, 200)
        self.assertIn("Del", str(res.data)) 

    # =================================================================
    # 5. ANALYTICS TESTS
    # =================================================================

    def test_analytics_dashboard_calculates_correct_totals(self):
        """Verify analytics correctly sums up monthly costs across different frequencies."""
        # Create 2 subscriptions: $10 Monthly + $120 Yearly ($10/mo)
        self.client.post('/subscriptions', json={"name": "Sub1", "price": 10, "frequency": "Monthly", "category": "Fun"})
        self.client.post('/subscriptions', json={"name": "Sub2", "price": 120, "frequency": "Yearly", "category": "Work"})

        res = self.client.get('/analytics')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)

        # Expected Total Monthly: 10 + (120/12) = 20
        self.assertEqual(data['financial_summary']['total_monthly_cost'], 20.00)
        self.assertEqual(data['financial_summary']['active_subscription_count'], 2)
        
        # Verify Category Breakdown
        cats = data['category_insights']['all_category_totals']
        self.assertEqual(cats['Fun'], 10.00)
        self.assertEqual(cats['Work'], 10.00)

if __name__ == "__main__":
    unittest.main()