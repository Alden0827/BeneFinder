# Pantawid Beneficiary Search & Verification (Finder App)

This is a standalone Flask-based replica of the Beneficiary Finder menu.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Login Flask-Bcrypt requests captcha python-dotenv psycopg2-binary
   ```

2. Configure environment variables:
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```

3. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5001`.

## Features
- Fuzzy search for beneficiaries using PostgreSQL `similarity`.
- Household roster view with grantee highlighting.
- Secure login with image CAPTCHA and 'Remember Me' (cookie-based).
- Modern UI built with Tailwind CSS.
- LDAP/API integration for authentication.
