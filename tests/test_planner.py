"""Unit-тесты планировщика: без сети, детерминированы."""

from app.services.geo import get_destination
from app.services.planner import build_estimate, build_itinerary, build_plan, packing_list


def test_paris_city_plan_numbers() -> None:
    dest = get_destination("Paris")
    plan = build_plan(dest, days=3, budget=1500, style="city", interests=["museums", "food"])
    assert plan.destination == "Paris"
    assert plan.days == 3
    assert len(plan.itinerary) == 3
    total_items = sum(len(day.items) for day in plan.itinerary)
    assert total_items == 6
    # Отель 120*3 + еда 60*3 + активности 123 = 663.
    assert plan.estimate.total == 663.0
    assert plan.estimate.hotel == 360.0
    assert plan.estimate.food == 180.0
    assert plan.estimate.activities == 123.0
    assert plan.estimate.within_budget is True
    assert "Comfortable shoes" in plan.packing


def test_relax_style_prefers_relax() -> None:
    dest = get_destination("Bali")
    itinerary = build_itinerary(dest, days=2, interests=[], style="relax")
    assert itinerary[0].items[0].startswith("Beach Day")
    assert "Swimwear" in packing_list(2, "relax")


def test_unknown_city_fallback() -> None:
    dest = get_destination("Atlantis")
    assert dest.name == "Atlantis"
    assert dest.hotel_per_day == 100.0
    assert dest.food_per_day == 50.0
    plan = build_plan(dest, days=2, budget=100, style="city", interests=[])
    assert plan.estimate.within_budget is False


def test_long_trip_packing() -> None:
    assert "Laundry kit" in packing_list(10, "city")
    assert "Laundry kit" not in packing_list(3, "city")


def test_estimate_standalone() -> None:
    dest = get_destination("Tokyo")
    itinerary = build_itinerary(dest, days=1, interests=[], style="city")
    estimate = build_estimate(dest, 1, itinerary, budget=1000, currency="USD")
    # Отель 110 + еда 55 + активности 25+35 = 225.
    assert estimate.total == 225.0
    assert estimate.within_budget is True
