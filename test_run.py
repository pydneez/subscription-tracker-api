import unittest
import json
from app import create_app, db
from app.models import Subscription, Category, FrequencyType, StatusType

class SubscriptionTrackerTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test variables and initialize app."""
        # Use a separate test config to avoid messing up your real DB
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # In-memory DB
        self.client = self.app.test_client()
        
        # Create tables within the application context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # =================================================================
    # 1. CATEGORY TESTS
    # =================================================================

    def test_create_category_manual(self):
        """Test manually creating a category via POST /categories"""
        res = self.client.post('/categories', json={"name": "Gaming"})
        self.assertEqual(res.status_code, 201)
        self.assertIn("Gaming", str(res.data))

    def test_create_duplicate_category(self):
        """Test that creating a duplicate category fails"""
        self.client.post('/categories', json={"name": "Music"})
        res = self.client.post('/categories', json={"name": "Music"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("already exists", str(res.data))

    def test_get_all_categories(self):
        """Test retrieving list of categories"""
        with self.app.app_context():
            db.session.add(Category(name="Tech"))
            db.session.commit()

        res = self.client.get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Tech")

    # =================================================================
    # 2. SUBSCRIPTION SUCCESS TESTS
    # =================================================================

    def test_create_subscription_auto_category(self):
        """Test creating subscription automatically creates the category"""
        payload = {
            "name": "Netflix",
            "price": 15.99,
            "frequency": "Monthly",
            "category": "Entertainment", # This category doesn't exist yet
            "status": "Active"
        }
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 201)
        
        # Verify it created the category
        with self.app.app_context():
            cat = Category.query.filter_by(name="Entertainment").first()
            self.assertIsNotNone(cat)

    def test_get_all_subscriptions(self):
        """Test getting all subscriptions"""
        # Seed data
        with self.app.app_context():
            c = Category(name="Gym")
            db.session.add(c)
            db.session.commit()
            s = Subscription(name="Planet Fitness", price=10, frequency=FrequencyType.MONTHLY, category_id=c.id)
            db.session.add(s)
            db.session.commit()

        res = self.client.get('/subscriptions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Planet Fitness")

    def test_filter_subscriptions_by_category(self):
        """Test filtering: GET /subscriptions?category=Gaming"""
        with self.app.app_context():
            c1 = Category(name="Gaming")
            c2 = Category(name="Food")
            db.session.add_all([c1, c2])
            db.session.commit()
            
            s1 = Subscription(name="Xbox", price=15, frequency=FrequencyType.MONTHLY, category_id=c1.id)
            s2 = Subscription(name="Taco Bell", price=20, frequency=FrequencyType.WEEKLY, category_id=c2.id)
            db.session.add_all([s1, s2])
            db.session.commit()

        # Filter for Gaming
        res = self.client.get('/subscriptions?category=Gaming')
        data = json.loads(res.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Xbox")

        # Filter for Non-existent category
        res_empty = self.client.get('/subscriptions?category=SpaceTravel')
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(json.loads(res_empty.data)['subscriptions'], [])

    def test_update_subscription(self):
        """Test updating price and status"""
        # Create initial
        with self.app.app_context():
            c = Category(name="Music")
            db.session.add(c)
            db.session.commit()
            s = Subscription(name="Spotify", price=10, frequency=FrequencyType.MONTHLY, category_id=c.id)
            db.session.add(s)
            db.session.commit()

        # Update
        payload = {"price": 12.99, "status": "Cancelled"}
        res = self.client.put('/subscriptions/1', json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        
        self.assertEqual(data['subscription']['price'], 12.99)
        self.assertEqual(data['subscription']['status'], "Cancelled")

    def test_delete_subscription(self):
        """Test deleting a subscription"""
        with self.app.app_context():
            c = Category(name="News")
            db.session.add(c)
            db.session.commit()
            s = Subscription(name="NYT", price=5, frequency=FrequencyType.WEEKLY, category_id=c.id)
            db.session.add(s)
            db.session.commit()

        res = self.client.delete('/subscriptions/1')
        self.assertEqual(res.status_code, 200)

        # Confirm it's gone
        res_check = self.client.get('/subscriptions/1')
        self.assertEqual(res_check.status_code, 404)

    # =================================================================
    # 3. ERROR HANDLING & EDGE CASES
    # =================================================================

    def test_create_missing_fields(self):
        """Test 400 Bad Request when fields are missing"""
        payload = {"name": "Incomplete"} # Missing price, frequency, category
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing required fields", str(res.data))

    def test_create_negative_price(self):
        """Test validation for negative price"""
        payload = {
            "name": "Bad Price",
            "price": -50.00,
            "frequency": "Monthly",
            "category": "Test"
        }
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Price must be a positive number", str(res.data))

    def test_invalid_enum_value(self):
        """Test validation for invalid Frequency Enum"""
        payload = {
            "name": "Bad Enum",
            "price": 10,
            "frequency": "Daily", # Invalid!
            "category": "Test"
        }
        res = self.client.post('/subscriptions', json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid frequency", str(res.data))

    def test_get_nonexistent_id(self):
        """Test 404 when ID doesn't exist"""
        res = self.client.get('/subscriptions/999')
        self.assertEqual(res.status_code, 404)
        self.assertIn("Subscription with ID 999 not found", str(res.data))

    def test_update_nonexistent_id(self):
        """Test 404 when updating a missing ID"""
        res = self.client.put('/subscriptions/999', json={"price": 20})
        self.assertEqual(res.status_code, 404)

    def test_delete_nonexistent_id(self):
        """Test 404 when deleting a missing ID"""
        res = self.client.delete('/subscriptions/999')
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()