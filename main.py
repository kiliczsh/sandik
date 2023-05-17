from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass

import aiohttp

MAX_RETRIES = 20


logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)


class RemoteEntity:
    def __init__(self, session) -> None:
        self.session = session

    async def fetch(self, url) -> list[dict]:
        try_no = 0
        while try_no < MAX_RETRIES:
            try:
                logging.debug("Sending request to %s (try: %s)", url, try_no)
                async with self.session.get(url, raise_for_status=True) as response:
                    logging.debug("%s finished with status %s", url, response.status)
                    return await response.json()
            except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError) as e:
                if (
                    isinstance(e, aiohttp.ClientConnectorError)
                    or e.status == 429
                    or e.status == 500
                ):
                    logging.info(
                        "Sleeping before retry for %s (try: %s)...", url, try_no
                    )
                    await asyncio.sleep(0.1 * 2**try_no)
                else:
                    logging.error("%s failed with code %s", url, e.status)
                    raise e
            try_no += 1
        raise RuntimeError(f"Max retries reached for {url}: {try_no}")


@dataclass
class School(RemoteEntity):
    id: int
    name: str
    neighborhood_id: int

    def __init__(self, session, id, name, city_id, district_id, neighborhood_id):
        super().__init__(session)
        self.id = id
        self.name = name
        self.city_id = city_id
        self.district_id = district_id
        self.neighborhood_id = neighborhood_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "district_id": self.district_id,
            "neighborhood_id": self.neighborhood_id,
        }

    def __str__(self):
        return f"{self.id} - {self.name} - {self.city_id} - {self.district_id} - {self.neighborhood_id}"


@dataclass
class Neighborhood(RemoteEntity):
    id: int
    name: str
    city_id: int
    district_id: int
    schools: list[School]

    @property
    def schools_url(self):
        return f"https://api-sonuc.oyveotesi.org/api/v1/cities/{self.city_id}/districts/{self.district_id}/neighborhoods/{self.id}/schools"

    def __init__(self, session, id, name, city_id, district_id):
        super().__init__(session)
        self.id = id
        self.name = name
        self.city_id = city_id
        self.district_id = district_id
        self.schools = []

    async def download(self) -> Neighborhood:
        self.schools = [
            School(
                self.session,
                id=school["id"],
                name=school["name"],
                city_id=self.city_id,
                district_id=self.district_id,
                neighborhood_id=self.id,
            )
            for school in await self.fetch(self.schools_url)
        ]
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "district_id": self.district_id,
            "schools": [school.to_dict() for school in self.schools],
        }

    def __str__(self):
        return f"{self.id} - {self.name}"


@dataclass
class District(RemoteEntity):
    id: int
    name: str
    city_id: int
    neighborhoods: list[Neighborhood]

    @property
    def neighborhoods_url(self):
        return f"https://api-sonuc.oyveotesi.org/api/v1/cities/{self.city_id}/districts/{self.id}/neighborhoods"

    def __init__(self, session, id, name, city_id):
        super().__init__(session)
        self.id = id
        self.name = name
        self.city_id = city_id
        self.neighborhoods = []

    async def download(self) -> District:
        self.neighborhoods = await asyncio.gather(
            *(
                Neighborhood(
                    self.session,
                    id=neighborhood["id"],
                    name=neighborhood["name"],
                    city_id=self.city_id,
                    district_id=self.id,
                ).download()
                for neighborhood in await self.fetch(self.neighborhoods_url)
            )
        )
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "neighborhoods": [
                neighborhood.to_dict() for neighborhood in self.neighborhoods
            ],
        }

    def __str__(self):
        return f"{self.id} - {self.name} - {len(self.neighborhoods)}"


@dataclass
class City(RemoteEntity):
    id: int
    name: str
    plate: int
    districts: list[District]

    @property
    def districts_url(self):
        return f"https://api-sonuc.oyveotesi.org/api/v1/cities/{self.id}/districts"

    def __init__(self, session, id, name, plate):
        super().__init__(session)
        self.id = id
        self.name = name
        self.plate = plate
        self.districts = []

    async def download(self) -> City:
        self.districts = await asyncio.gather(
            *(
                District(
                    self.session,
                    id=district["id"],
                    name=district["name"],
                    city_id=self.id,
                ).download()
                for district in await self.fetch(self.districts_url)
            )
        )
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "plate": self.plate,
            "districts": [district.to_dict() for district in self.districts],
        }

    def __str__(self):
        return f"{self.id} - {self.name} - {self.plate} - {len(self.districts)}"


async def gather_all(session):
    cities = await get_cities(session)
    print_cities(cities)
    print("Gathered all cities")


def print_cities(cities):
    cities_dict = [city.to_dict() for city in cities]

    with open("tree.json", "w", encoding="utf-8") as f:
        json.dump(cities_dict, f, ensure_ascii=False, indent=4)


async def get_cities(session):
    with open("cities.json", "r", encoding="utf-8") as f:
        cities_json = json.load(f)

    cities = await asyncio.gather(
        *(
            City(session, id=city["id"], name=city["name"], plate=plate).download()
            for plate, city in cities_json.items()
        )
    )

    return cities


async def main():
    with open("cities.json", "r", encoding="utf-8") as f:
        cities_json = json.load(f)

    city_plate = int(input("Enter city plate: "))

    if city_plate not in cities_json:
        print("Error: city not found")
        exit(1)

    city_data = cities_json[city_plate]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        city = await City(
            session, id=city_data["id"], name=city_data["name"], plate=int(city_plate)
        ).download()

    filename = f"{city.name}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(city.to_dict(), f, ensure_ascii=False, indent=4)

    print(f"Wrote to {filename}")

    print(f"Gathered city {city.name}")


if __name__ == "__main__":
    asyncio.run(main())
