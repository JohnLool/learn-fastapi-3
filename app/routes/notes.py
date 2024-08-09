from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/", response_model=schemas.NoteOut)
async def create_note(user_id: int, note: Annotated[schemas.NoteCreate, Depends()], db: AsyncSession = Depends(get_db)):
    db_note = models.Note(**note.dict(), owner_id=user_id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.put("/{note_id}", response_model=schemas.NoteOut)
async def update_note(note_id: int, user_id: int, note: schemas.NoteCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == user_id))
    db_note = result.scalar_one_or_none()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    for key, value in note.dict().items():
        setattr(db_note, key, value)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.delete("/{note_id}")
async def delete_note(note_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == user_id))
    db_note = result.scalar_one_or_none()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(db_note)
    await db.commit()
    return {"detail": "Note deleted"}


@router.get("/", response_model=list[schemas.NoteOut])
async def get_notes(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Note).filter(models.Note.owner_id == user_id))
    notes = result.scalars().all()
    return notes
