from datetime import date as DateType
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import RecordType, UserRole, UserStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    role: UserRole = UserRole.viewer
    status: UserStatus = UserStatus.active


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    role: UserRole | None = None
    status: UserStatus | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime


ALLOWED_CATEGORIES = {
    "Salary",
    "Groceries",
    "Rent",
    "Utilities",
    "Investment",
    "Transport",
    "Other",
}


class RecordBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: RecordType
    category: str
    date: DateType
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_be_allowed(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")
        return value


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2)
    type: RecordType | None = None
    category: str | None = None
    date: DateType | None = None
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_be_allowed(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")
        return value


class RecordRead(RecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class SummaryTotals(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal


class CategorySummary(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: str
    total_income: Decimal
    total_expenses: Decimal
    net: Decimal
