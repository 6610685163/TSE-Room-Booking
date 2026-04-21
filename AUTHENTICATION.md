# TSE Room Booking System - Authentication Module Implementation

## Overview

This document describes the implementation of the authentication system for the TSE Room Booking System according to SRS requirements FR-AUTH-01 through FR-AUTH-05.

## Requirements Implemented

### FR-AUTH-01: TU REST API Login
- ✅ Users can login using Thammasat University credentials
- ✅ Supports Username/Password combination
- ✅ Integrates with TU REST API

### FR-AUTH-02: TU REST API Integration
- ✅ POST request to `https://restapi.tu.ac.th/api/v1/auth/Ad/verify`
- ✅ Headers: `Content-Type: application/json`, `Application-Key: {token}`
- ✅ Request body: `{ "UserName": "{username}", "PassWord": "{password}" }`

### FR-AUTH-03: Session Management
- ✅ Session created after successful authentication
- ✅ Session stored in database (default Django session backend)
- ✅ No need to re-login for each request

### FR-AUTH-04: Logout
- ✅ Users can logout and destroy session
- ✅ Session data cleared from database

### FR-AUTH-05: Role Assignment
- ✅ Two roles: Lecturer (อาจารย์) and Admin (เจ้าหน้าที่)
- ✅ Admin can assign roles to users
- ✅ Role-based access control implemented

## Project Structure

```
Users/
├── models.py                 # UserProfile and Room models
├── views.py                  # Authentication views
├── forms.py                  # Login and role assignment forms
├── auth_backend.py          # TU REST API authentication backend
├── admin.py                 # Django admin configuration
├── apps.py                  # App configuration
├── templates/Users/
│   ├── login.html           # Login form
│   ├── dashboard_lecturer.html
│   ├── dashboard_admin.html
│   ├── assign_role.html
│   └── users_management.html
└── migrations/              # Database migrations
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Django 6.0.4
- requests 2.31.0
- python-dotenv 1.0.0
- psycopg2-binary 2.9.9 (for PostgreSQL support)

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Critical Settings:**
```
TU_API_KEY=your-tu-api-key-here
TU_API_ENDPOINT=https://restapi.tu.ac.th/api/v1/auth/Ad/verify
```

To get your Application-Key:
1. Visit https://restapi.tu.ac.th
2. Register for API access
3. Copy your Application-Key

### 3. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the following tables:
- `auth_user` (Django built-in)
- `Users_userprofile` (Custom user profile)
- `Users_room` (Room information)

### 4. Create Admin User

```bash
python manage.py createsuperuser
```

### 5. Load Initial Room Data

```bash
# SQL INSERT statements for the 5 rooms:
INSERT INTO Users_room (room_code, room_name, room_type, capacity, is_active) VALUES
('406-3', 'ห้องประชุม 1', 'meeting', 60, TRUE),
('406-5', 'ห้องประชุม 2', 'meeting', 15, TRUE),
('408-1', 'ห้องประชุม 3', 'meeting', 10, TRUE),
('408-2/1', 'ห้องบรรยาย 1', 'classroom', 20, TRUE),
('408-2/2', 'ห้องบรรยาย 2', 'classroom', 20, TRUE);
```

Or use Django admin: http://localhost:8000/admin/

### 6. Run Development Server

```bash
python manage.py runserver
```

Access at: http://localhost:8000/

## Authentication Flow

```
User Login
    ↓
Input Username/Password (TU credentials)
    ↓
POST to TU REST API → Verify Credentials
    ↓
Credentials Valid?
    ├─ YES → Check if user exists in database
    │         ├─ User exists → Load user
    │         └─ First login → Create user profile (default role: Lecturer)
    │         ↓
    │         Create Session → Redirect to Dashboard
    │
    └─ NO → Display error message → Back to Login
```

## Key Components

### 1. Authentication Backend (`auth_backend.py`)

Custom authentication backend that:
- Validates credentials against TU REST API
- Creates/updates local user records on successful login
- Handles API errors gracefully
- Logs authentication events

**Main Methods:**
- `authenticate()`: Main authentication method
- `_verify_tu_credentials()`: Verifies against TU REST API
- `get_user()`: Retrieves user by ID

### 2. Models (`models.py`)

**UserProfile Model:**
```python
- user (OneToOneField to Django User)
- tu_username (unique TU username)
- role (Lecturer or Admin)
- full_name
- email
- is_active
- created_at, updated_at
```

**Room Model:**
```python
- room_code (unique identifier)
- room_name (Thai name)
- room_type (meeting/classroom)
- capacity (number of seats)
- description
- is_active
- created_at, updated_at
```

### 3. Views (`views.py`)

- `login_view()`: Login form and authentication
- `logout_view()`: Session destruction
- `dashboard_view()`: Main dashboard (role-specific)
- `assign_user_role_view()`: Admin role assignment
- `users_management_view()`: Admin user management

### 4. Forms (`forms.py`)

- `TULoginForm`: Login form validation
- `UserRoleAssignmentForm`: Role assignment form

## Security Features (NFR-SEC)

### NFR-SEC-01: No Password Storage
- Passwords are **never** stored locally
- Authentication always delegated to TU REST API
- Local database only stores user profile and role info

### NFR-SEC-02: HTTPS Communication
- Development: Uses HTTP (configure HTTPS for production)
- Production: Must use HTTPS with proper SSL certificates
- Use settings: `SECURE_SSL_REDIRECT = True`

### NFR-SEC-03: Session Timeout
- Session timeout: **8 hours** (28,800 seconds)
- Configurable in `settings.py`: `SESSION_COOKIE_AGE`
- Automatic logout after timeout

### NFR-SEC-04: CSRF & XSS Protection
- CSRF token used in all forms ({% csrf_token %})
- Django template auto-escaping prevents XSS
- SQL injection prevented via ORM (no raw SQL)

## Usage Examples

### Login Flow
```
1. Visit http://localhost:8000/login/
2. Enter TU username (e.g., student ID)
3. Enter TU password
4. System validates against TU API
5. If valid → Session created → Dashboard displayed
6. If invalid → Error message → Back to login
```

### Role Assignment (Admin Only)
```
1. Admin visits /users/ (Users Management)
2. Sees list of all users
3. Clicks "แก้ไขบทบาท" (Edit Role)
4. Selects new role (Lecturer/Admin)
5. Clicks "บันทึก" (Save)
6. System logs the change
```

### Logout
```
1. User clicks "ออกจากระบบ" (Logout)
2. Session destroyed
3. Redirect to login page
```

## Configuration for Production

### 1. Environment Variables
```bash
DEBUG=False
SECRET_KEY=generate-a-strong-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. HTTPS/SSL
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Database
```bash
# Use PostgreSQL instead of SQLite
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=tse_booking
DATABASE_USER=dbuser
DATABASE_PASSWORD=dbpassword
DATABASE_HOST=database-server
DATABASE_PORT=5432
```

### 4. Email Configuration
```python
# For email notifications (FR-NOTI-01, FR-NOTI-02)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
```

### 5. Logging
Logs are stored in `logs/` directory:
- `authentication.log`: Authentication events
- `tse_booking.log`: General application logs

## Error Handling

### Common Authentication Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid credentials" | Wrong username/password | Check TU credentials |
| "TU API unavailable" | Network issue or API down | Check internet connection, try again later |
| "User not found" | First login → auto-create | Normal flow, user profile created automatically |
| "Insufficient permissions" | Non-admin trying admin feature | Only admins can assign roles |

## Logging

The system logs all authentication events:

```python
# Example log entries
logger.info(f"User {username} logged in successfully")
logger.warning(f"Login failed for user: {username}")
logger.error(f"TU REST API authentication failed: {error}")
```

View logs in:
- Console output (development)
- `logs/authentication.log` (all servers)
- `logs/tse_booking.log` (general app logs)

## Testing

### Manual Testing

1. **Test successful login:**
   - Visit `/login/`
   - Use valid TU credentials
   - Verify redirect to `/dashboard/`

2. **Test failed login:**
   - Use invalid credentials
   - Verify error message displayed

3. **Test logout:**
   - Click logout button
   - Verify redirect to login
   - Verify session destroyed

4. **Test role assignment:**
   - Login as admin
   - Visit `/users/`
   - Change user role
   - Verify change reflected

### Unit Testing

Run tests:
```bash
python manage.py test Users
```

## Future Enhancements

Planned for future versions:
- Two-factor authentication (2FA)
- Remember me functionality
- Session management (view active sessions)
- Login history and audit logs
- IP whitelisting for admin accounts
- SSO integration with other systems

## Troubleshooting

### Issue: "Cannot connect to TU REST API"
**Solutions:**
- Check internet connection
- Verify TU_API_KEY is correct
- Check firewall/proxy settings
- Verify TU API is online at https://restapi.tu.ac.th

### Issue: "Module 'requests' not found"
**Solution:**
```bash
pip install -r requirements.txt
pip install requests
```

### Issue: "Database locked" (SQLite)
**Solutions:**
- Switch to PostgreSQL for production
- Restart Django development server
- Delete `db.sqlite3` and migrate again (development only)

### Issue: "Session expires immediately"
**Solution:**
Check `SESSION_COOKIE_AGE` in settings.py (should be 28800 for 8 hours)

## Support & Documentation

- SRS Document: See project repository
- TU REST API Docs: https://restapi.tu.ac.th
- Django Documentation: https://docs.djangoproject.com/

## Compliance with SRS

| Requirement | Status | Implementation |
|-------------|--------|-----------------|
| FR-AUTH-01 | ✅ Complete | TURestAPIBackend class |
| FR-AUTH-02 | ✅ Complete | _verify_tu_credentials() method |
| FR-AUTH-03 | ✅ Complete | Django session middleware |
| FR-AUTH-04 | ✅ Complete | logout_view() |
| FR-AUTH-05 | ✅ Complete | UserProfile.role field |
| NFR-SEC-01 | ✅ Complete | TU API verification only |
| NFR-SEC-02 | ⚠️ Partial | Configure for HTTPS in production |
| NFR-SEC-03 | ✅ Complete | 8-hour session timeout |
| NFR-SEC-04 | ✅ Complete | Django built-in protection |

---

**Last Updated:** April 21, 2026
**Version:** 1.0
