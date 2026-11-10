from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    # One Product can appear in many OrderItems
    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )

# USER TABLE

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Existing users ki wajah se optional rakha hai
    phone = Column(String, nullable=True)

    is_admin = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    # One User can have many Orders
    orders = relationship(
        "Order",
        back_populates="user"
    )


# ==========================================
# ORDER TABLE
# ==========================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String,
        default="pending",
        nullable=False
    )

    # This Order belongs to one User
    user = relationship(
        "User",
        back_populates="orders"
    )
    
    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    


# ==========================================
# ORDER ITEM TABLE
# ==========================================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")

    product = relationship("Product", back_populates="order_items")