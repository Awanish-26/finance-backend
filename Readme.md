# Finance Data Processing and Access Control Backend

Build a REST API for managing financial records with Role-Based Access Control (RBAC). Store users with different roles (Admin, Analyst, Viewer), manage financial records, perform soft deletions, and aggregate financial summaries.

### API structure and there format

- **POST /api/auth/login** — Authenticate and receive a JWT token
  - Body: `{ email: string, password: string }`
  - Response `200`: `{ access_token: string, token_type: "bearer" }`
  - Response `401`: incorrect email or password

- **GET /api/auth/me** — Get current authenticated user details
  - Response `200`: object of current user
  - Example : `{  "id": int,  "email": "user@example.com",  "name": "string",  "role": "viewer",  "status": "active",  "created_at": "2026-04-06T13:55:18.155Z",  "updated_at": "2026-04-06T13:55:18.155Z"}`

- **POST /api/users** — Create a new user (Admin only)
  - Body: `{ email: string, name: string, role: string, password: string }`
  - Validate `role` is one of `admin`, `analyst`, `viewer`
  - Response `201`: created user object
  - Response `400`: missing or invalid fields
  - Response `409`: email already exists
  - Response `403`: forbidden for non-admins

- **GET /api/users** — List all users (Admin only)
  - Response `200`: array of users

- **GET /api/users/:id** — Get a specific user (Admin or Self)
  - Response `200`: user object
  - Response `403`: forbidden
  - Response `404`: user not found

- **PATCH /api/users/:id** — Update user details
  - Body: `{ name: string, role: string, status: string }` (Users can update name; Admins can update roles/status)
  - Response `200`: updated user
  - Response `403`: forbidden for role/status updates if not admin

- **DELETE /api/users/:id** — Deactivate a user (Admin only)
  - Response `204`: user deactivated (soft delete)
  - Response `403`: forbidden if not admin

### Financial Records CRUD

- **POST /api/records** — Create a new financial record (Analyst and Admin only)
  - Body: `{ amount: number, type: "income" | "expense", category: string, date: string, notes: string }`
  - Response `201`: created financial record
  - Response `403`: forbidden for viewers

- **GET /api/records** — List records
  - Query param: `?type=income` or `?category=food` (optional filters)
  - Response `200`: array of financial records

- **GET /api/records/:id** — Get a specific record
  - Response `200`: record object
  - Response `404`: record not found

- **PATCH /api/records/:id** — Update a record (Owner Analyst or Admin)
  - Body: `{ amount: number, category: string, notes: string }`
  - Response `200`: updated record
  - Response `403`: forbidden if not owner or admin

- **DELETE /api/records/:id** — Soft delete a record (Owner Analyst or Admin)
  - Response `204`: record deleted
  - Response `403`: forbidden if not owner or admin

### Financial Summaries (Viewers, Analysts, Admins)

- **GET /api/summaries/totals** — Get total income, expenses, and net balance
  - Response `200`: `{ total_income: number, total_expenses: number, net_balance: number }`

- **GET /api/summaries/by-category** — Get aggregated totals grouped by category
  - Response `200`: array of `{ category: string, total: number }`

- **GET /api/summaries/recent** — Fetch the most recent financial activities
  - Response `200`: array of recent financial records

- **GET /api/summaries/trends** — Fetch monthly/weekly income vs. expenses trends
  - Response `200`: array of trend data objects

## Notes

- Users are assigned roles: `viewer` (read-only), `analyst` (manage own records), `admin` (full access)
- Records use a `deleted_at` timestamp for soft deletions to ensure data retention
- Seed the database with `python seed.py` which will insert dummy users (admin, analyst, viewer) and records
