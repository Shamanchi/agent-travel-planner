"""Построение маршрута, сметы и чек-листа."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.geo import Attraction, Destination


class DayPlan(BaseModel):
    day: int
    items: list[str] = []


class Estimate(BaseModel):
    hotel: float
    food: float
    activities: float
    total: float
    budget: float
    within_budget: bool
    currency: str


class TripPlan(BaseModel):
    destination: str
    days: int
    style: str
    itinerary: list[DayPlan]
    estimate: Estimate
    packing: list[str]


def _order_attractions(
    attractions: list[Attraction], interests: list[str], style: str
) -> list[Attraction]:
    wanted = {tag.strip().lower() for tag in interests if tag.strip()}
    if not wanted:
        matched = list(attractions)
        rest: list[Attraction] = []
    else:
        matched = [a for a in attractions if wanted & {t.lower() for t in a.tags}]
        rest = [a for a in attractions if not (wanted & {t.lower() for t in a.tags})]
    if style == "relax":
        matched.sort(key=lambda a: (not a.relax_ok, a.name))
        rest.sort(key=lambda a: (not a.relax_ok, a.name))
    return matched + rest


def build_itinerary(destination: Destination, days: int, interests: list[str], style: str) -> list[DayPlan]:
    """Разложить достопримечательности по дням (round-robin). Детерминировано."""
    if days < 1:
        raise ValueError("days must be >= 1")
    ordered = _order_attractions(destination.attractions, interests, style)
    plan = [DayPlan(day=day, items=[]) for day in range(1, days + 1)]
    for i, attraction in enumerate(ordered):
        tag = attraction.tags[0] if attraction.tags else "visit"
        plan[i % days].items.append(f"{attraction.name} ({tag}, {attraction.cost:g})")
    return plan


def build_estimate(
    destination: Destination,
    days: int,
    itinerary: list[DayPlan],
    budget: float,
    currency: str = "USD",
) -> Estimate:
    """Посчитать смету. Стоимость активностей извлекается из known-аттракций."""
    by_name = {a.name: a.cost for a in destination.attractions}
    activities = 0.0
    for day in itinerary:
        for item in day.items:
            name = item.split(" (")[0]
            activities += by_name.get(name, 0.0)
    hotel = round(destination.hotel_per_day * days, 2)
    food = round(destination.food_per_day * days, 2)
    activities = round(activities, 2)
    total = round(hotel + food + activities, 2)
    return Estimate(
        hotel=hotel,
        food=food,
        activities=activities,
        total=total,
        budget=budget,
        within_budget=total <= budget,
        currency=currency,
    )


BASE_PACKING = ["Passport", "Phone charger", "Medications"]
CITY_PACKING = ["Comfortable shoes", "Power adapter"]
RELAX_PACKING = ["Sunscreen", "Swimwear"]


def packing_list(days: int, style: str) -> list[str]:
    """Чек-лист сборов по стилю и длительности."""
    items = list(BASE_PACKING)
    items.extend(RELAX_PACKING if style == "relax" else CITY_PACKING)
    if days > 7:
        items.append("Laundry kit")
    return items


def build_plan(
    destination: Destination,
    days: int,
    budget: float,
    style: str,
    interests: list[str],
    currency: str = "USD",
) -> TripPlan:
    """Собрать полный план: маршрут + смета + чек-лист."""
    itinerary = build_itinerary(destination, days, interests, style)
    estimate = build_estimate(destination, days, itinerary, budget, currency)
    return TripPlan(
        destination=destination.name,
        days=days,
        style=style,
        itinerary=itinerary,
        estimate=estimate,
        packing=packing_list(days, style),
    )
