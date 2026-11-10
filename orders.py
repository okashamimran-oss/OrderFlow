from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from model import Order, User
from schemas import OrderResponse, FullOrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_own_order(order_id: int, db: Session, user: User) -> Order:
    # Sirf wahi order milega jo isi user ka ho
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


#--- ORDER CREATE ---
@router.post("/", response_model=OrderResponse)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_order = Order(user_id=current_user.id)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


#--- GET MY ORDERS ---
@router.get("/", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()


#--- GET ORDER DETAILS ---
@router.get("/{order_id}/details", response_model=FullOrderResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_own_order(order_id, db, current_user)

    items = []
    total = 0

    for item in order.order_items:
        price = item.unit_price
        subtotal = price * item.quantity
        total += subtotal

        items.append({
            "product_id": item.product_id,
            "product_name": item.product.name,
            "price": price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return {
        "id": order.id,
        "status": order.status,
        "user_id": order.user_id,
        "customer_name": order.user.name,
        "phone": order.user.phone,
        "items": items,
        "total": total
    }


#--- GET ORDER BY ID ---
@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_own_order(order_id, db, current_user)


#--- DELETE ORDER ---
@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    order = get_own_order(order_id, db, current_user)

    # Items delete hone se pehle stock wapas karo
    for item in order.order_items:
        item.product.stock += item.quantity

    db.delete(order)
    db.commit()