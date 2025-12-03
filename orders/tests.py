from django.test import TestCase

# Create your tests here.
# orders/tests.py
from django.test import TestCase
from tenants.models import Tenant
from users.models import User
from products.models import Product
from rest_framework.test import APIClient
from decimal import Decimal

class OrderPlacementTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(store_name="T1", contact_email="t1@example.com")
        self.user = User.objects.create_user(username="cust", email="c@t.com", password="pass", role="customer", tenant=self.tenant)
        self.product = Product.objects.create(tenant=self.tenant, name="P1", sku="SKU1", price=Decimal("10.00"), stock=5)
        self.client = APIClient()

        # create token via simplejwt utilities (or use test client login)
        from users.tokens import get_tokens_for_user
        tokens = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])

    def test_place_order_success(self):
        resp = self.client.post("/api/orders/", {"items":[{"product_id": str(self.product.id), "qty": 2}]}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
