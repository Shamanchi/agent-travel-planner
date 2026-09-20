"""Mock-база направлений: офлайн-фикстуры без сети."""

from __future__ import annotations

from pydantic import BaseModel


class Attraction(BaseModel):
    name: str
    tags: list[str] = []
    cost: float = 0.0
    relax_ok: bool = False


class Destination(BaseModel):
    name: str
    hotel_per_day: float
    food_per_day: float
    attractions: list[Attraction] = []


_DESTINATIONS: dict[str, Destination] = {
    "paris": Destination(
        name="Paris",
        hotel_per_day=120.0,
        food_per_day=60.0,
        attractions=[
            Attraction(name="Louvre", tags=["museums"], cost=20.0),
            Attraction(name="Eiffel Tower", tags=["sightseeing"], cost=30.0),
            Attraction(name="Montmartre Walk", tags=["sightseeing"], cost=0.0, relax_ok=True),
            Attraction(name="Seine Cruise", tags=["relax"], cost=15.0, relax_ok=True),
            Attraction(name="Orsay Museum", tags=["museums"], cost=18.0),
            Attraction(name="Le Marais Food Tour", tags=["food"], cost=40.0),
        ],
    ),
    "tokyo": Destination(
        name="Tokyo",
        hotel_per_day=110.0,
        food_per_day=55.0,
        attractions=[
            Attraction(name="Senso-ji Temple", tags=["sightseeing"], cost=0.0, relax_ok=True),
            Attraction(name="TeamLab Museum", tags=["museums"], cost=25.0),
            Attraction(name="Tsukiji Food Walk", tags=["food"], cost=35.0),
            Attraction(name="Shibuya Crossing", tags=["sightseeing"], cost=0.0),
            Attraction(name="Ueno Park", tags=["relax"], cost=0.0, relax_ok=True),
        ],
    ),
    "bali": Destination(
        name="Bali",
        hotel_per_day=60.0,
        food_per_day=30.0,
        attractions=[
            Attraction(name="Uluwatu Temple", tags=["sightseeing"], cost=10.0),
            Attraction(name="Beach Day", tags=["relax"], cost=0.0, relax_ok=True),
            Attraction(name="Spa Session", tags=["relax"], cost=25.0, relax_ok=True),
            Attraction(name="Rice Terraces", tags=["sightseeing"], cost=5.0, relax_ok=True),
        ],
    ),
}


def list_destinations() -> list[str]:
    return sorted(dest.name for dest in _DESTINATIONS.values())


def get_destination(name: str, hotel_per_day: float = 100.0, food_per_day: float = 50.0) -> Destination:
    """Найти направление или вернуть generic-профиль для неизвестного города."""
    key = name.strip().lower()
    if key in _DESTINATIONS:
        return _DESTINATIONS[key]
    title = name.strip().title() or "Unknown"
    return Destination(
        name=title,
        hotel_per_day=hotel_per_day,
        food_per_day=food_per_day,
        attractions=[
            Attraction(name="City center walk", tags=["sightseeing"], cost=0.0, relax_ok=True),
            Attraction(name="Local market", tags=["food"], cost=0.0, relax_ok=True),
            Attraction(name="City museum", tags=["museums"], cost=15.0),
        ],
    )
