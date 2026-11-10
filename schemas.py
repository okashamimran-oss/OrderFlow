from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


# ---------- Products ----------
class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Users ----------
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserOrderInfo(BaseModel):
    name: str
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Orders ----------
class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    user: UserOrderInfo

    model_config = ConfigDict(from_attributes=True)


class OrderInfo(BaseModel):
    status: str
    user: UserOrderInfo

    model_config = ConfigDict(from_attributes=True)


class OrderItemDetail(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float


class FullOrderResponse(BaseModel):
    id: int
    status: str
    user_id: int
    customer_name: str
    phone: str | None = None
    items: list[OrderItemDetail]
    total: float


# ---------- Order items ----------
class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(gt=0)


class ProductOrderInfo(BaseModel):
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    product: ProductOrderInfo
    order: OrderInfo

    @computed_field
    @property
    def subtotal(self) -> float:
        return round(self.unit_price * self.quantity, 2)

    model_config = ConfigDict(from_attributes=True)