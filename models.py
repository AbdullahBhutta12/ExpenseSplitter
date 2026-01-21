from sqlalchemy import (
    Column, Integer, String, Float,
    ForeignKey, DateTime, BOOLEAN, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    profile_image = Column(String, nullable=True)
    is_verified = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("Emails", back_populates="users", cascade="all, delete")
    groups = relationship("Group", back_populates="owner", cascade="all, delete")


class Emails(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    verification_code = Column(String, nullable=True)
    expiration_time = Column(DateTime(timezone=True), server_default=func.now())
    is_verified = Column(BOOLEAN, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    users = relationship("User", back_populates="emails")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="groups")
    participants = relationship("Participant", back_populates="group", cascade="all, delete")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    group_id = Column(Integer, ForeignKey("groups.id"))

    group = relationship("Group", back_populates="participants")
    expenses_paid = relationship("Expense", back_populates="paid_by")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    group_id = Column(Integer, ForeignKey("groups.id"))
    paid_by_id = Column(Integer, ForeignKey("participants.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="expenses")
    paid_by = relationship("Participant", back_populates="expenses_paid")