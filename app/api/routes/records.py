from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db import get_db
from app.models import FinancialRecord, RecordType, User, UserRole
from app.schemas import RecordCreate, RecordRead, RecordUpdate

router = APIRouter()


def _can_modify_record(current_user: User, record: FinancialRecord) -> bool:
    if current_user.role == UserRole.admin:
        return True
    if current_user.role == UserRole.analyst and record.user_id == current_user.id:
        return True
    return False


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.analyst, UserRole.admin)),
):
    record = FinancialRecord(
        user_id=current_user.id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[RecordRead])
def list_records(
    start_date: date | None = Query(default=None, alias="startDate"),
    end_date: date | None = Query(default=None, alias="endDate"),
    category: str | None = None,
    type: RecordType | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="startDate cannot be after endDate")

    filters = [FinancialRecord.deleted_at.is_(None)]

    if current_user.role != UserRole.admin:
        filters.append(FinancialRecord.user_id == current_user.id)

    if start_date:
        filters.append(FinancialRecord.date >= start_date)
    if end_date:
        filters.append(FinancialRecord.date <= end_date)
    if category:
        filters.append(FinancialRecord.category == category)
    if type:
        filters.append(FinancialRecord.type == type)

    offset = (page - 1) * limit

    stmt = (
        select(FinancialRecord)
        .where(and_(*filters))
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


@router.get("/{record_id}", response_model=RecordRead)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.get(FinancialRecord, record_id)
    if not record or record.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    if current_user.role != UserRole.admin and record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")

    return record


@router.patch("/{record_id}", response_model=RecordRead)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.analyst, UserRole.admin)),
):
    record = db.get(FinancialRecord, record_id)
    if not record or record.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    if not _can_modify_record(current_user, record):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(record, key, value)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.analyst, UserRole.admin)),
):
    record = db.get(FinancialRecord, record_id)
    if not record or record.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    if not _can_modify_record(current_user, record):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")

    record.deleted_at = datetime.utcnow()
    db.add(record)
    db.commit()
    return None
