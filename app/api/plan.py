"""Эндпоинты планирования поездок."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.geo import get_destination, list_destinations
from app.services.planner import Estimate, TripPlan, build_estimate, build_itinerary, build_plan

router = APIRouter()

Style = Literal["city", "relax"]


class PlanRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=100)
    days: int = Field(ge=1, le=60)
    budget: float = Field(gt=0, le=10_000_000)
    style: Style = "city"
    interests: list[str] = Field(default_factory=list, max_length=20)


class EstimateRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=100)
    days: int = Field(ge=1, le=60)
    budget: float = Field(gt=0, le=10_000_000)
    style: Style = "city"
    interests: list[str] = Field(default_factory=list, max_length=20)


@router.get("/destinations")
async def destinations() -> dict:
    return {"destinations": list_destinations()}


@router.post("/plan", response_model=TripPlan)
async def create_plan(
    request: PlanRequest,
    settings: Settings = Depends(get_settings),
) -> TripPlan:
    if request.days > settings.max_days:
        raise HTTPException(status_code=422, detail=f"days must be <= {settings.max_days}")
    destination = get_destination(
        request.destination,
        hotel_per_day=settings.default_hotel_per_day,
        food_per_day=settings.default_food_per_day,
    )
    return build_plan(
        destination,
        request.days,
        request.budget,
        request.style,
        request.interests,
        currency=settings.default_currency,
    )


@router.post("/estimate", response_model=Estimate)
async def create_estimate(
    request: EstimateRequest,
    settings: Settings = Depends(get_settings),
) -> Estimate:
    if request.days > settings.max_days:
        raise HTTPException(status_code=422, detail=f"days must be <= {settings.max_days}")
    destination = get_destination(
        request.destination,
        hotel_per_day=settings.default_hotel_per_day,
        food_per_day=settings.default_food_per_day,
    )
    itinerary = build_itinerary(destination, request.days, request.interests, request.style)
    return build_estimate(
        destination, request.days, itinerary, request.budget, settings.default_currency
    )
