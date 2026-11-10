import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from limiter import limiter
from router import products, users, orders, order_items

app = FastAPI(title="OrderFlow API")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


@app.middleware("http")
async def measure_response_time(request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response


app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(order_items.router)


@app.get("/")
def home():
    return {"message": "OrderFlow API running"}


@app.get("/health")
def health():
    return {"status": "ok"}