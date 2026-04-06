from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
from app.models import FinancialRecord, RecordType, User, UserRole, UserStatus


SEED_USERS = [
    {
        "email": "admin@example.com",
        "name": "Admin User",
        "role": UserRole.admin,
        "status": UserStatus.active,
        "password": "Admin@123",
    },
    {
        "email": "analyst@example.com",
        "name": "Analyst User",
        "role": UserRole.analyst,
        "status": UserStatus.active,
        "password": "Analyst@123",
    },
    {
        "email": "viewer@example.com",
        "name": "Viewer User",
        "role": UserRole.viewer,
        "status": UserStatus.active,
        "password": "Viewer@123",
    },
]


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for user_data in SEED_USERS:
            user = db.execute(select(User).where(User.email == user_data["email"])).scalar_one_or_none()
            if not user:
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    role=user_data["role"],
                    status=user_data["status"],
                    password_hash=hash_password(user_data["password"]),
                )
                db.add(user)
                db.flush()

                if user.role in (UserRole.admin, UserRole.analyst):
                    db.add_all(
                        [
                            FinancialRecord(
                                user_id=user.id,
                                amount=Decimal("6000.00"),
                                type=RecordType.income,
                                category="Salary",
                                date=date(2026, 1, 10),
                                notes="Monthly salary",
                            ),
                            FinancialRecord(
                                user_id=user.id,
                                amount=Decimal("900.50"),
                                type=RecordType.expense,
                                category="Rent",
                                date=date(2026, 1, 12),
                                notes="House rent",
                            ),
                            FinancialRecord(
                                user_id=user.id,
                                amount=Decimal("300.00"),
                                type=RecordType.expense,
                                category="Groceries",
                                date=date(2026, 1, 15),
                                notes="Supermarket",
                            ),
                        ]
                    )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
    print("Seed data inserted.")
