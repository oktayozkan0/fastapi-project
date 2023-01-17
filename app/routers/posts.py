from .. import models, schemas
from typing import List
from fastapi import (
                    Response,
                    status,
                    HTTPException,
                    Depends,
                    APIRouter)
from sqlalchemy.orm import Session
from ..database import get_dba
from .. import oauth2


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.Post])
def get_all_posts(
    db: Session = Depends(get_dba),
    current_user: int = Depends(oauth2.get_current_user)
):
    print(current_user.email)
    posts = db.query(models.Post).all()
    return posts


@router.post("/create", response_model=schemas.PostCreate)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_dba),
    current_user: int = Depends(oauth2.get_current_user)
):
    # new_post = models.Post(
    #   title=post.title,
    #   content=post.content,
    #   is_published=post.is_published
    # )
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_one_post(
    id: int,
    db: Session = Depends(get_dba),
    current_user: int = Depends(oauth2.get_current_user)
):
    print(current_user.email)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.delete("/{id}")
def delete_post_by_id(
    id: int,
    db: Session = Depends(get_dba),
    current_user: int = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if current_user.id != post_query.first().owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can not delete others posts"
        )

    post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_dba),
    current_user: int = Depends(oauth2.get_current_user)
):
    print(current_user.email)
    post_q = db.query(models.Post).filter(models.Post.id == id)

    if post_q.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post_q.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_q.first()
