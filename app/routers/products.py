from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.schemas import CreateProduct
from app.models import Category
from app.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product).where(Product.is_active == True, Product.stock > 0)
    )
    all_products = products.all()
    if not all_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no products",
        )
    return all_products


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    created_product: CreateProduct,
    get_user: Annotated[dict, Depends(get_current_user)],
):

    if get_user.get("is_admin") or get_user.get("is_supplier"):
        category = await db.scalar(
            select(Category).where(Category.id == created_product.category)
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no category found",
            )
        await db.execute(
            insert(Product).values(
                name=created_product.name,
                description=created_product.description,
                price=created_product.price,
                image_url=created_product.image_url,
                stock=created_product.stock,
                supplier_id=get_user.get("id"),
                category_id=created_product.category,
                rating=0.0,
                slug=slugify(created_product.name),
                sum_rewies=0,
                count_rewies=0,
            )
        )
        await db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )


@router.get("/{category_slug}")
async def product_by_category(
    db: Annotated[AsyncSession, Depends(get_db)], category_slug: str
):
    category = await db.scalar(
        select(Category).where(
            Category.slug == category_slug, Category.is_active == True
        )
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    subcategories = await db.scalars(
        select(Category).where(Category.parent_id == category.id)
    )
    categories_and_subcategories = [category.id] + [i.id for i in subcategories.all()]
    products_in_category = await db.scalars(
        select(Product).where(
            Product.category_id.in_(categories_and_subcategories),
            Product.is_active == True,
            Product.stock > 0,
        )
    )
    return products_in_category.all()


@router.get("/detail/{product_slug}")
async def product_detail(
    db: Annotated[AsyncSession, Depends(get_db)], product_slug: str
):
    product = await db.scalar(
        select(Product).where(
            Product.slug == product_slug,
            Product.is_active == True,
            Product.stock > 0,
        )
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such product",
        )
    return product


@router.put("/detail/{product_slug}")
async def update_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    updated_product: CreateProduct,
    get_user: Annotated[dict, Depends(get_current_user)],
):

    if not (get_user.get("is_admin") or get_user.get("is_supplier")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )

    product_upd = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_upd is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )

    if not (product_upd.supplier_id == get_user.get("id") or get_user.get("is_admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )

    category = await db.scalar(
        select(Category).where(Category.id == updated_product.category)
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no category found"
        )

    await db.execute(
        update(Product)
        .where(Product.slug == product_slug)
        .values(
            name=updated_product.name,
            slug=slugify(updated_product.name),
            description=updated_product.description,
            price=updated_product.price,
            image_url=updated_product.image_url,
            stock=updated_product.stock,
            supplier_id=get_user.get("id"),
            category_id=updated_product.category,
        )
    )
    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product update is successful",
    }


@router.delete("/delete")
async def delete_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    get_user: Annotated[dict, Depends(get_current_user)],
):

    if not (get_user.get("is_admin") or get_user.get("is_supplier")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )

    product_del = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_del is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )

    if product_del.supplier_id != get_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )

    await db.execute(
        update(Product).where(Product.slug == product_slug).values(is_active=False)
    )
    # await db.delete(product_del)  # для реального удаления

    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product delete is successful",
    }
