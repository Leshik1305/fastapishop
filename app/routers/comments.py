from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.comments import Comment
from app.schemas import CreateComment
from app.routers.auth import get_current_user


router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/")
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    comments = await db.scalars(select(Comment).where(Comment.is_active == True))
    all_comments = comments.all()
    if not all_comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no comments",
        )
    return all_comments


@router.get("/{product_slug}")
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug):
    product = await db.scalar(
        select(Product).where(
            Product.is_active == True,
            Product.slug == product_slug,
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such product",
        )
    comments = await db.scalars(
        select(Comment).where(
            Comment.is_active == True,
            Comment.product_id == product.id,
        )
    )
    all_comments = comments.all()
    if not all_comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no comments",
        )

    return all_comments


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    created_comment: CreateComment,
    # updated_product: UpdateProduct,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_customer"):
        product = await db.scalar(
            select(Product).where(Product.id == created_comment.product_id)
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="There is no such product"
            )

        await db.execute(
            insert(Comment).values(
                user_id=get_user.get("id"),
                comment=created_comment.comment,
                comment_date=created_comment.comment_date,
                product_id=created_comment.product_id,
                grade=created_comment.grade,
            )
        )
        # Хотел в модели Product сделать список всех оценок и из него считать среднее арифметическое, но не разобрался организовать подсчет тут,
        # пришлось вводить две дополнительные колонки в таблицу продуктов, с общей суммой оценок и количеством
        await db.execute(
            update(Product)
            .where(Product.id == created_comment.product_id)
            .values(
                rating=(Product.sum_rewies + created_comment.grade)
                / (
                    Product.count_rewies + 1
                ),  # как тут можно округлить до знака после запятой? или это нужно прописовать в модели?
                sum_rewies=Product.sum_rewies + created_comment.grade,
                count_rewies=Product.count_rewies + 1,
            )
        )

        await db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be customer for this",
        )


@router.delete("/{id}")
async def delete_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    comment_id: int,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if not (get_user.get("is_admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be admin user for this",
        )
    comment_del = await db.scalar(
        select(Comment).where(Comment.id == comment_id, Comment.is_active == True)
    )
    if comment_del is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such comment",
        )
    await db.execute(
        update(Comment).where(Comment.id == comment_id).values(is_active=False)
    )
    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Comment delete is successful",
    }
