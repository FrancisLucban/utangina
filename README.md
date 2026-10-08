# UT@NGINA

*Because apparently our friend group needed financial stability*

A personal project created for my circle to simply keep track of who owes who, built with Django and PostgreSQL.

## Features

- **Accounts** — register, log in, log out, with a custom UUID-based user model
- **Debt tracking** — log debts in either direction, with an optional due date, phone number, and description
- **Partial payments** — record payments against a debt and watch the remaining balance update automatically; debts settle themselves once fully paid
- **Dashboard** — search, filter (active / I owe / owed to me / settled), sort (date, due date, name, amount), and paginate
- **At-a-glance totals** — total owed, total receivable, net balance, and an overdue count
- **Soft delete** — deleted debts and payments are recoverable from the Django admin, never actually gone
- **Toast notifications** for every meaningful action
- **Responsive UI** styled with Tailwind CSS

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Django |
| Database | PostgreSQL |
| Frontend | Django templates + Tailwind CSS (CLI build, no CDN) |
| Auth | Custom user model (UUIDv7 primary keys) |
| Deployment | Render (gunicorn + whitenoise) |

## Getting started

### Prerequisites

- Python 3.11+
- Node.js (for the Tailwind build)
- PostgreSQL

### Setup

```bash
# Clone and enter the project
git clone https://github.com/<your-username>/debt-manager.git
cd debt-manager/debtmanager

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend tooling
npm install

# Environment variables
cp .env.example .env   # then fill in your own values

# Database
createdb debtmanager_db
python manage.py migrate
python manage.py createsuperuser

# Build Tailwind CSS
npm run build:css
```

### Running locally

In two terminal tabs:

```bash
python manage.py runserver
```

```bash
npm run watch:css
```

Visit `http://127.0.0.1:8000`.

## Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` locally, `False` in production |
| `DATABASE_URL` | `postgres://user:password@host:port/dbname` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |

## Deployment

Configured for [Render](https://render.com) out of the box — see `build.sh` and `Procfile`. Push to `main` and Render handles the rest: installs dependencies, builds Tailwind, collects static files, and runs migrations.

## Project structure

```
debtmanager/
├── accounts/        # Custom user model
├── debts/           # Core app — models, views, forms, templates
├── debtmanager/     # Project settings, URLs
├── static_src/      # Tailwind source CSS
├── templates/        # Project-level templates (base, auth, debts)
├── build.sh          # Render build script
└── Procfile           # Render start command
```

## License

Personal project, built for learning Django.
