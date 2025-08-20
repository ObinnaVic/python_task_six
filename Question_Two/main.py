from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List
import json
import os
from auth import require_admin, require_authenticated

app = FastAPI(title="Shopping Cart API", version="1.0.0")

PRODUCTS_FILE = "products.json"
CART_FILE = "cart.json"

class User(BaseModel):
    username: str
    role: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str
    stock: int

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    stock: int

class CartItem(BaseModel):
    username: str
    product_id: int
    quantity: int

class CartAdd(BaseModel):
    product_id: int
    quantity: int

def load_products():
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading products file: {e}")
        return []

def save_products(products_data):
    try:
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(products_data, f, indent=2)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving products data: {str(e)}"
        )

def load_cart():
    try:
        if os.path.exists(CART_FILE):
            with open(CART_FILE, 'r') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading cart file: {e}")
        return []

def save_cart(cart_data):
    try:
        with open(CART_FILE, 'w') as f:
            json.dump(cart_data, f, indent=2)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving cart data: {str(e)}"
        )

def get_next_product_id():
    products = load_products()
    if not products:
        return 1
    return max(p["id"] for p in products) + 1

@app.get("/")
def root():
    return {"message": "Shopping Cart API"}

@app.post("/admin/add_product/", response_model=dict)
def add_product(product: ProductCreate, admin_user: dict = Depends(require_admin)):
    products = load_products()
    
    new_product = {
        "id": get_next_product_id(),
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "stock": product.stock
    }
    
    products.append(new_product)
    save_products(products)
    
    return {"message": "Product added successfully", "product": new_product}

@app.get("/products/", response_model=List[Product])
def get_products():
    products = load_products()
    return products

@app.post("/cart/add/", response_model=dict)
def add_to_cart(cart_item: CartAdd, user: dict = Depends(require_authenticated)):
    products = load_products()
    cart = load_cart()
    
    product = next((p for p in products if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Available: {product['stock']}"
        )
    
    cart_entry = {
        "username": user["username"],
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
        "product_name": product["name"],
        "unit_price": product["price"],
        "total_price": product["price"] * cart_item.quantity
    }
    
    cart.append(cart_entry)
    save_cart(cart)
    
    return {"message": "Item added to cart successfully", "cart_item": cart_entry}

@app.get("/cart/", response_model=List[dict])
def get_user_cart(user: dict = Depends(require_authenticated)):
    cart = load_cart()
    user_cart = [item for item in cart if item["username"] == user["username"]]
    return user_cart

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)