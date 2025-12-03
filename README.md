Run Locally (Without Docker)
1. Create Python virtual environment:
python -m venv venv


Activate it:

venv\Scripts\activate     (Windows)
source venv/bin/activate  (Mac/Linux)

2. Install dependencies:
pip install -r requirements.txt

3. Setup PostgreSQL locally:

Create a database:

Database name: multitenant
User: postgres
Password:12345678
Host: localhost
Port: 5432

4. Apply migrations:
python manage.py makemigrations
python manage.py migrate

5. Run the development server:
python manage.py runserver

📡 API Endpoints
🔐 Authentication
Register (Creates Tenant + Owner)
POST http://localhost:8000/api/auth/register/

Login
POST http://localhost:8000/api/auth/login/

Refresh Token
POST /api/auth/refresh/

📦 Product APIs
List all products (tenant-scoped)
GET http://localhost:8000/api/products/

Create product
POST http://localhost:8000/api/products/

Retrieve product
GET http://localhost:8000/api/products/<id>/

Update product
PUT http://localhost:8000/api/products/<id>/

Delete product
DELETE http://localhost:8000/api/products/<id>/

🧾 Order APIs
List orders (Owner/Staff)
GET http://localhost:8000/api/orders/

Place order (Customer)
POST http://localhost:8000/api/orders/

Retrieve order
GET http://localhost:8000/api/orders/<id>/

# How Multi-Tenancy Works

Multi-tenancy is implemented using:

1️⃣ Tenant Model

Each vendor has a separate Tenant object.

2️⃣ User → Tenant Relationship

Every user belongs to exactly one tenant:

tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

3️⃣ JWT Token Includes Tenant ID

During authentication, the tenant_id is added to JWT:

token["tenant_id"] = user.tenant.id
token["role"] = user.role


Every request now knows:

Which tenant the user belongs to

What role the user has

4️⃣ Tenant Filtering in Views

Every queryset is filtered by tenant:

queryset = Product.objects.filter(tenant=request.user.tenant)


This ensures users can only access data belonging to their tenant.

# How Role-Based Access Works
1️⃣ Role Assigned to Every User

Roles: owner, staff, customer

2️⃣ Custom DRF Permissions

Example:

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "owner"


Used in views like:

permission_classes = [IsAuthenticated, IsOwner]

Access Levels:
Role	Permissions
Owner	Add/edit/delete products, view all orders
Staff	Manage products/orders assigned to them
Customer	View products & place orders


# postman collection JSON

{
  "info": {
    "name": "Multi-Tenant E-Commerce Platform",
    "_postman_id": "a12b345c-d678-910e-fgh1-234567890xyz",
    "description": "Postman Collection for Multi-Tenant E-Commerce Platform (Django + DRF + JWT)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register Owner (Creates Tenant)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n    \"username\": \"owner1\",\n    \"email\": \"owner1@example.com\",\n    \"password\": \"pass12345\",\n    \"store_name\": \"Vendor One Store\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/auth/register/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "auth", "register", ""]
            }
          },
          "response": [],
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "var json = pm.response.json();",
                  "pm.environment.set(\"access_token\", json.access);",
                  "pm.environment.set(\"refresh_token\", json.refresh);",
                  "pm.environment.set(\"tenant_id\", json.tenant.id);"
                ]
              }
            }
          ]
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"owner1\",\n  \"password\": \"pass12345\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/auth/login/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "auth", "login", ""]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "var json = pm.response.json();",
                  "pm.environment.set(\"access_token\", json.access);",
                  "pm.environment.set(\"refresh_token\", json.refresh);"
                ]
              }
            }
          ]
        },
        {
          "name": "Refresh Token",
          "request": {
            "method": "POST",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"refresh\": \"{{refresh_token}}\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/auth/refresh/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "auth", "refresh", ""]
            }
          }
        }
      ]
    },

    {
      "name": "Products",
      "item": [
        {
          "name": "Create Product",
          "request": {
            "method": "POST",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" },
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Laptop\",\n  \"sku\": \"LAP100\",\n  \"price\": 1200,\n  \"stock\": 5,\n  \"description\": \"High-speed laptop\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/products/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "products", ""]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.environment.set(\"product_id\", pm.response.json().id);"
                ]
              }
            }
          ]
        },
        {
          "name": "List Products",
          "request": {
            "method": "GET",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" }
            ],
            "url": {
              "raw": "http://localhost:8000/api/products/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "products", ""]
            }
          }
        },
        {
          "name": "Get Product by ID",
          "request": {
            "method": "GET",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" }
            ],
            "url": {
              "raw": "http://localhost:8000/api/products/{{product_id}}/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "products", "{{product_id}}", ""]
            }
          }
        },
        {
          "name": "Update Product",
          "request": {
            "method": "PUT",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" },
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Laptop Pro\",\n  \"sku\": \"LAP200\",\n  \"price\": 1500,\n  \"stock\": 10,\n  \"description\": \"Updated description\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/products/{{product_id}}/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "products", "{{product_id}}", ""]
            }
          }
        },
        {
          "name": "Delete Product",
          "request": {
            "method": "DELETE",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" }
            ],
            "url": {
              "raw": "http://localhost:8000/api/products/{{product_id}}/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "products", "{{product_id}}", ""]
            }
          }
        }
      ]
    },

    {
      "name": "Orders",
      "item": [
        {
          "name": "Place Order (Customer)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{customer_access_token}}"
              },
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"items\": [\n    { \"product_id\": \"{{product_id}}\", \"qty\": 2 }\n  ]\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/orders/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "orders", ""]
            }
          }
        },
        {
          "name": "List Orders",
          "request": {
            "method": "GET",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" }
            ],
            "url": {
              "raw": "http://localhost:8000/api/orders/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "orders", ""]
            }
          }
        },
        {
          "name": "Get Order by ID",
          "request": {
            "method": "GET",
            "header": [
              { "key": "Authorization", "value": "Bearer {{access_token}}" }
            ],
            "url": {
              "raw": "http://localhost:8000/api/orders/{{order_id}}/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "orders", "{{order_id}}", ""]
            }
          }
        }
      ]
    }
  ],
  "event": [],
  "variable": []
}
