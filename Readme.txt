# FastAPI Projects Collection

This repository contains 4 secure FastAPI projects demonstrating different authentication and authorization patterns.

## Projects Overview

1. **Student Portal API** - HTTP Basic Auth for grade management
2. **Shopping Cart API** - Role-based access with admin controls  
3. **Job Application Tracker** - User isolation with secure data access
4. **Notes Management API** - JWT token authentication

---

## Project 1: Student Portal API

A secure API where students can register, login, and view their grades.

### Features
- Student registration with password hashing
- HTTP Basic Authentication
- Secure grade viewing
- JSON file storage with error handling

### Files
- `main.py` - Main API application
- `students.json` - Auto-created student data storage
- `requirements.txt` - Dependencies

### Endpoints
- `POST /register/` - Register new student
- `POST /login/` - Authenticate student  
- `GET /grades/` - View grades (requires auth)

### Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py

# Example: Register student
POST /register/
{
  "username": "john",
  "password": "pass123",
  "grades": [85.5, 92.0, 78.5]
}

# Example: Get grades (with Basic Auth)
GET /grades/
Authorization: Basic john:pass123
```

---

## Project 2: Shopping Cart API with Admin Access

A shopping API with role-based access control where admins manage products and customers shop.

### Features
- Admin and customer roles
- Separate authentication module
- Product management (admin only)
- Shopping cart functionality
- Dependency injection for role checking

### Files
- `main.py` - Main shopping API
- `auth.py` - Authentication and role management
- `users.json` - User accounts (auto-created)
- `products.json` - Product catalog
- `cart.json` - Shopping cart data

### Default Users
- **Admin**: username=`admin`, password=`admin123`
- **Customer**: username=`user1`, password=`user123`

### Endpoints
- `POST /admin/add_product/` - Add products (admin only)
- `GET /products/` - Browse products (public)
- `POST /cart/add/` - Add to cart (authenticated users)
- `GET /cart/` - View cart items

### Usage
```bash
pip install -r requirements.txt
python main.py

# Add product (admin only)
POST /admin/add_product/
Authorization: Basic admin:admin123
{
  "name": "Laptop",
  "price": 999.99,
  "description": "Gaming laptop",
  "stock": 10
}

# Add to cart (any authenticated user)
POST /cart/add/
Authorization: Basic user1:user123
{
  "product_id": 1,
  "quantity": 2
}
```

---

## Project 3: Job Application Tracker

A secure API where users can only access their own job applications.

### Features
- Complete user data isolation
- Job application CRUD operations
- Secure filtering by current user
- HTTP Basic Authentication
- Per-user data protection

### Files
- `main.py` - Job tracker API
- `auth.py` - User authentication
- `users.json` - User accounts (auto-created)
- `applications.json` - All job applications

### Default Users
- **john**: password=`john123`
- **jane**: password=`jane123`

### Endpoints
- `POST /applications/` - Add job application
- `GET /applications/` - View YOUR applications only
- `GET /applications/{id}` - Get specific application (yours only)
- `PUT /applications/{id}` - Update your application
- `DELETE /applications/{id}` - Delete your application

### Usage
```bash
pip install -r requirements.txt
python main.py

# Add job application
POST /applications/
Authorization: Basic john:john123
{
  "job_title": "Software Engineer",
  "company": "Google", 
  "date_applied": "2025-08-20",
  "status": "applied"
}

# View your applications (only shows john's applications)
GET /applications/
Authorization: Basic john:john123
```

---

## Project 4: Notes Management API

A notes API using JWT token authentication for secure access.

### Features
- JWT Bearer token authentication
- Per-user note storage
- Token-based security
- Separate JSON files per user
- 30-minute token expiration

### Files
- `main.py` - Notes API
- `auth.py` - JWT token management
- `users.json` - User accounts (auto-created)
- `notes_{username}.json` - Per-user note files

### Default Users
- **john**: password=`john123`
- **jane**: password=`jane123`

### Endpoints
- `POST /login/` - Get JWT access token
- `POST /notes/` - Add note (requires token)
- `GET /notes/` - View your notes (requires token)

### Usage
```bash
pip install -r requirements.txt
python main.py

# 1. Login to get token
POST /login/
{
  "username": "john",
  "password": "john123"
}

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Add note with token
POST /notes/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
{
  "title": "Meeting Notes",
  "content": "Discussed project requirements",
  "date": "2025-08-20"
}

# 3. Get notes with token
GET /notes/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Common Dependencies

All projects require these packages:

```txt
fastapi==0.104.1
uvicorn==0.24.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

**Additional for Project 4 (Notes API):**
```txt
python-jose[cryptography]==3.3.0
```

## Installation & Setup

1. **Clone/Download the project files**

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run any project:**
   ```bash
   python main.py
   ```

5. **Access the API:**
   - API runs on: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

## Security Features

### Authentication Methods Used:
- **HTTP Basic Auth** (Projects 1, 2, 3) - Username/password in headers
- **JWT Bearer Tokens** (Project 4) - Token-based authentication

### Security Measures:
- **Password Hashing** - All passwords encrypted with bcrypt
- **User Isolation** - Users can only access their own data
- **Role-based Access** - Admin/customer roles (Project 2)
- **Token Expiration** - JWT tokens expire after 30 minutes
- **Error Handling** - Proper HTTP status codes and error messages

## Testing the APIs

### Using curl:
```bash
# Basic Auth example
curl -X GET "http://localhost:8000/grades/" \
  -H "Authorization: Basic $(echo -n 'john:pass123' | base64)"

# Bearer Token example  
curl -X GET "http://localhost:8000/notes/" \
  -H "Authorization: Bearer your-jwt-token-here"
```

