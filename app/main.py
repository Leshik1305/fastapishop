from fastapi import FastAPI
from app.routers import category, products, auth, permission, comments

app = FastAPI()


@app.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app1"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(comments.router)
