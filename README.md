# 📊 SubTrack API (Subscription Tracker)

A RESTful API built with **Python** and **Flask** to help users track recurring expenses, manage subscriptions, and calculate monthly spending. This project demonstrates modular software architecture using Flask Blueprints and SQLAlchemy.

## 🚀 Features

* **CRUD Operations:** Create, Read, Update, and Delete subscriptions.
* **Advanced Filtering:** Filter subscriptions by category and status (e.g., `GET /subscriptions?category=Gaming&status=active`).
* **Financial Analytics:** Real-time dashboard calculating monthly spend, yearly projections, and top spending categories.
* **Budget Tracking:** Set a monthly limit and get health alerts (e.g., "Over Budget", "Warning").
* **Data Validation:** Enforces strict Enum types for Frequencies and Statuses to ensure data integrity.

---

## 📂 Project Structure

```text
/subscription-tracker
│
├── run.py                 # Entry Point (Run this to start server)
├── seed.py                # Database Seeder (Run this to reset data)
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── .gitignore             # Git ignore rules
│
├── instance/              # Local Data Folder (Ignored by Git)
│   └── subscriptions.db   # SQLite Database File
│
└── app/                   # Main Application Package
    ├── __init__.py        # App Factory & Initialization
    ├── models.py          # Database Models & Enums
    └── routes/            # API Route Blueprints
        ├── __init__.py
        ├── analytics.py   # Financial Dashboard Logic
        ├── budgets.py     # Budget Management Logic
        ├── category.py    # Category CRUD
        └── subscription.py # Subscription CRUD
```
---

## ⚡ Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/pydneez/subscription-tracker-api
cd subscription-tracker-api

```

### 2. Set up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Initialize the Database

Run the seed script to create the database tables and populate them with sample data (e.g., Netflix, Spotify).

```bash
python seed.py

```

*> Expected Output: "✅ Database seeded!"*

### 5. Run the Server

```bash
python run.py

```


---

## 📡 API Endpoints

### 1. Subscriptions

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/subscriptions` | Retrieve all subscriptions. |
| **GET** | `/subscriptions?category=Name` | Filter subscriptions by category and/or status (e.g., `?category=Gamin&status=active`). |
| **GET** | `/subscriptions/<id>` | Retrieve a single subscription by ID. |
| **POST** | `/subscriptions` | Create a new subscription. |
| **PUT** | `/subscriptions/<id>` | Update an existing subscription. |
| **DELETE** | `/subscriptions/<id>` | Delete a subscription. |

**📝 POST Request Example (Create):**

```json
{
  "name": "Netflix",
  "price": 15.99,
  "frequency": "Monthly",
  "category": "Entertainment",
  "status": "Active",
  "start_date": "2023-01-15"
}

```

**📝 PUT Request Example (Update):**

```json
{
  "price": 19.99,
  "status": "Cancelled"
}

```

---

### 2. Categories

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/categories` | List all available categories. |
| **POST** | `/categories` | Manually create a new category. |


---

### 3. Summarize prices (Per month)

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/analytics` | List total prices that are Active. |


---

### 4. Limit Budget

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/budget` | Show current budget. |
| **GET** | `/budget/status` | Show the status. |
| **PUT** | `/budget` | Limit the budget. |

**📝 PUT Request Example (Set Limit):**

```json
{
  "limit": 150
}


```
---
