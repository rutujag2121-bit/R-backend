# Secure DevOps - Backend (Flask)

CT5192 Assignment 2 — Backend service built with Python Flask.

## Stack
- Python 3.11
- Flask 3.0
- SQLite (demo database)
- pytest + pytest-cov (testing)

## Local Setup

```bash
pip install -r requirements.txt
python app/main.py
```

## Run Tests

```bash
pytest tests/ --cov=app --cov-report=xml
```

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | /health | Health check |
| POST | /api/login | User login |
| GET | /api/users | List users |
| POST | /api/users | Create user |
| GET | /api/search?q= | Search |
| GET | /api/ping?host= | Ping host |

## Security Tools Integrated
- **SonarCloud** — Static analysis on PRs and main branch
- **Snyk** — Dependency vulnerability scanning
- **ZAP** — Dynamic Application Security Testing (DAST)

## Intentional Vulnerabilities (for assignment)
1. SQL Injection in `/api/login` — detected by SonarQube
2. Hardcoded secret key — detected by SonarQube
3. MD5 password hashing — detected by SonarQube
4. Command injection in `/api/ping` — detected by SonarQube
5. Reflected XSS in `/api/search` — detected by ZAP
6. Wildcard CORS + debug mode — detected by ZAP
