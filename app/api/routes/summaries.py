from collections import defaultdict
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import FinancialRecord, RecordType, User, UserRole
from app.schemas import CategorySummary, RecordRead, SummaryTotals, TrendPoint

router = APIRouter()


def _build_filters(current_user: User, start_date: date | None, end_date: date | None):
    filters = [FinancialRecord.deleted_at.is_(None)]
    if current_user.role != UserRole.admin:
        filters.append(FinancialRecord.user_id == current_user.id)
    if start_date:
        filters.append(FinancialRecord.date >= start_date)
    if end_date:
        filters.append(FinancialRecord.date <= end_date)
    return filters


@router.get("/totals", response_model=SummaryTotals)
def totals(
    start_date: date | None = Query(default=None, alias="startDate"),
    end_date: date | None = Query(default=None, alias="endDate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="startDate cannot be after endDate")

    filters = _build_filters(current_user, start_date, end_date)

    income_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        and_(*filters, FinancialRecord.type == RecordType.income)
    )
    expenses_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        and_(*filters, FinancialRecord.type == RecordType.expense)
    )

    income = db.execute(income_stmt).scalar_one()
    expenses = db.execute(expenses_stmt).scalar_one()
    net = Decimal(income) - Decimal(expenses)

    return SummaryTotals(total_income=income, total_expenses=expenses, net_balance=net)


@router.get("/by-category", response_model=list[CategorySummary])
def by_category(
    start_date: date | None = Query(default=None, alias="startDate"),
    end_date: date | None = Query(default=None, alias="endDate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = _build_filters(current_user, start_date, end_date)
    stmt = (
        select(FinancialRecord.category, func.coalesce(
            func.sum(FinancialRecord.amount), 0))
        .where(and_(*filters))
        .group_by(FinancialRecord.category)
        .order_by(FinancialRecord.category.asc())
    )

    rows = db.execute(stmt).all()
    return [CategorySummary(category=category, total=total) for category, total in rows]


@router.get("/recent", response_model=list[RecordRead])
def recent(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = _build_filters(current_user, None, None)
    stmt = (
        select(FinancialRecord)
        .where(and_(*filters))
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


@router.get("/trends", response_model=list[TrendPoint])
def trends(
    start_date: date | None = Query(default=None, alias="startDate"),
    end_date: date | None = Query(default=None, alias="endDate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = _build_filters(current_user, start_date, end_date)

    stmt = select(FinancialRecord).where(
        and_(*filters)).order_by(FinancialRecord.date.asc())
    records = db.execute(stmt).scalars().all()

    buckets: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expense": Decimal("0")}
    )

    for record in records:
        period = record.date.strftime("%Y-%m")
        if record.type == RecordType.income:
            buckets[period]["income"] += Decimal(record.amount)
        else:
            buckets[period]["expense"] += Decimal(record.amount)

    response: list[TrendPoint] = []
    for period in sorted(buckets.keys()):
        income = buckets[period]["income"]
        expense = buckets[period]["expense"]
        response.append(
            TrendPoint(period=period, total_income=income,
                       total_expenses=expense, net=income - expense)
        )
    return response
