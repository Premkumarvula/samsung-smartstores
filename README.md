# Samsung SmartStore

A lightweight, production-ready e-commerce demo built with Flask, SQLAlchemy,
and vanilla HTML/CSS/JS — sized to run comfortably on an AWS EC2 t3.micro
instance (2 vCPU / 1GB RAM).

## Features

- Product catalog with detail pages
- Session-based shopping cart (add/update quantity/remove)
- User registration & login (Flask-Login, hashed passwords, CSRF-protected forms)
- Checkout flow that creates real `Order` / `OrderItem` records
- Order history per user
- Admin dashboard (product CRUD, order/revenue stats), protected by role check
- `/health` endpoint that also verifies the database connection
- Structured logging (console + rotating file) ready for Dynatrace log ingestion
- Custom 400/403/404/500 error pages

## Architecture

```
app/
  __init__.py         # application factory
  config.py           # env-driven Dev/Prod/Testing config
  extensions.py       # db, csrf, login_manager singletons
  models.py           # User, Product, Order, OrderItem
  forms.py            # WTForms validation
  logging_config.py
  seed_data.py
  blueprints/
    main/    -> home, product detail, health check
    auth/    -> register, login, logout
    cart/    -> cart CRUD, checkout
    orders/  -> order history & detail
    admin/   -> product management, dashboard
templates/            # Jinja2, all extending base.html
static/                # CSS + product images
wsgi.py                # Gunicorn entrypoint (production)
run.py                 # Flask dev server entrypoint (local only)
gunicorn.conf.py
deploy/
  nginx.conf
  smartstore.service    # systemd unit
.github/workflows/deploy.yml
```

## Local development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit SECRET_KEY

flask --app run seed-db   # or: python seed.py
python run.py             # http://localhost:5000
```

## Running with Gunicorn (production-style, locally)

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
gunicorn -c gunicorn.conf.py wsgi:app
```

## Deployment (AWS EC2, Amazon Linux 2023)

```
GitHub → GitHub Actions → EC2 → Gunicorn → Nginx → Dynatrace OneAgent
```

1. Provision a t3.micro, install Python 3.12, Nginx, and Dynatrace OneAgent.
2. Clone the repo to `/opt/smartstore`, create a venv, `pip install -r requirements.txt`.
3. Copy `.env.example` to `/opt/smartstore/.env` and fill in a real `SECRET_KEY`
   and `FLASK_ENV=production`.
4. Install the systemd service: `deploy/smartstore.service` → `/etc/systemd/system/`.
5. Install the Nginx site config: `deploy/nginx.conf` → `/etc/nginx/conf.d/`.
6. `systemctl enable --now smartstore && systemctl reload nginx`.
7. Set GitHub Actions secrets `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY` — every push
   to `main` will lint, smoke-test, then SSH in and redeploy.

## Creating an admin user

```bash
flask --app run create-admin
```

## Health check

`GET /health` returns `{"status": "UP", "database": "UP", ...}` (200) or 503 if
the database is unreachable — point Dynatrace synthetic monitors / the ALB
health check here.

# test

