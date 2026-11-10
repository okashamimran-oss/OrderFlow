from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from model import OrderItem, Order, Product, User
from schemas import OrderItemCreate, OrderItemResponse

router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


def get_own_order(order_id: int, db: Session, user: User) -> Order:
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


def get_own_item(item_id: int, db: Session, user: User) -> OrderItem:
    item = (
        db.query(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.id == item_id, Order.user_id == user.id)
        .first()
    )

    if item is None:
        raise HTTPException(status_code=404, detail="Order item not found")

    return item


#---CREATE ORDER ITEM---
@router.post("/", response_model=OrderItemResponse)
def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_own_order(item.order_id, db, current_user)

    product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == item.order_id,
        OrderItem.product_id == item.product_id
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
        result = existing_item
    else:
        result = OrderItem(
            order_id=item.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.add(result)

    product.stock = product.stock - item.quantity

    db.commit()
    db.refresh(result)

    return result


#--- GET MY ORDER ITEMS---
@router.get("/", response_model=list[OrderItemResponse])
def get_order_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.user_id == current_user.id)
        .all()
    )


#--- GET ORDER ITEM BY ID---
@router.get("/{item_id}", response_model=OrderItemResponse)
def get_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_own_item(item_id, db, current_user)


#--- ORDER ITEM UPDATE---
@router.put("/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    item_id: int,
    updated_item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = get_own_item(item_id, db, current_user)
    get_own_order(updated_item.order_id, db, current_user)

    old_product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    new_product = db.query(Product).filter(
        Product.id == updated_item.product_id
    ).first()

    if new_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if item.product_id == updated_item.product_id:
        available_stock = old_product.stock + item.quantity

        if available_stock < updated_item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        old_product.stock = available_stock - updated_item.quantity

    else:
        if new_product.stock < updated_item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        old_product.stock += item.quantity
        new_product.stock -= updated_item.quantity

        item.unit_price = new_product.price

    item.order_id = updated_item.order_id
    item.product_id = updated_item.product_id
    item.quantity = updated_item.quantity

    db.commit()
    db.refresh(item)

    return item


#--- DELETE ORDER ITEM ---
@router.delete("/{item_id}")
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = get_own_item(item_id, db, current_user)

    product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    if product:
        product.stock += item.quantity

    db.delete(item)
    db.commit()

    return {"message": "Order item deleted successfully"}