from dataclasses import dataclass
from enum import Enum
import json
import time
import requests

SLEEP_TIME = 1

class AreaType(Enum):
    CITY = 1
    DISTRICT = 2
    NEIGHBORHOOD = 3
    SCHOOL = 4
    SANDIK = 5

@dataclass
class School:
    id: int
    name: str
    neighborhood_id: int

    def __init__(self, id, name, city_id, district_id, neighborhood_id):
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
            "neighborhood_id": self.neighborhood_id
        }
    
    def __str__(self):
        return f"{self.id} - {self.name} - {self.city_id} - {self.district_id} - {self.neighborhood_id}"

@dataclass
class Neighborhood:
    id: int
    name: str
    city_id: int
    district_id: int
    schools: list[School]

    def __init__(self, id, name, city_id, district_id):
        self.id = id
        self.name = name
        self.city_id = city_id
        self.district_id = district_id
        self.schools = []
        schools = send_request(AreaType.SCHOOL, city_id=self.city_id, district_id=self.district_id, neighborhood_id=self.id)
        for school in schools:
            self.schools.append(School(id=school["id"], name=school["name"], city_id=self.city_id, district_id=self.district_id, neighborhood_id=self.id))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "district_id": self.district_id,
            "schools": [school.to_dict() for school in self.schools]
        }
    
    def __str__(self):
        return f"{self.id} - {self.name}"


@dataclass
class District:
    id: int
    name: str
    city_id: int
    neighborhoods: list[Neighborhood]

    def __init__(self, id, name, city_id):
        self.id = id
        self.name = name
        self.city_id = city_id
        self.neighborhoods = []
        neighborhoods = send_request(AreaType.NEIGHBORHOOD, city_id=self.city_id, district_id=self.id)
        for neighborhood in neighborhoods:
            self.neighborhoods.append(Neighborhood(id=neighborhood["id"], name=neighborhood["name"], city_id=self.city_id, district_id=self.id))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "neighborhoods": [neighborhood.to_dict() for neighborhood in self.neighborhoods]
        }
    
    def __str__(self):
        return f"{self.id} - {self.name} - {self.neighborhoods.count()}"


@dataclass
class City:
    id: int
    name: str
    plate: int
    districts: list[District]

    def __init__(self, id, name, plate):
        self.id = id
        self.name = name
        self.plate = plate
        self.districts = []
        districts = send_request(AreaType.DISTRICT, city_id=self.id)
        for district in districts:
            self.districts.append(District(id=district["id"], name=district["name"], city_id=self.id))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "plate": self.plate,
            "districts": [district.to_dict() for district in self.districts]
        }

    def __str__(self):
        return f"{self.id} - {self.name} - {self.plate} - {self.districts.count()}"

def send_request(type, city_id=0, district_id=0, neighborhood_id=0, school_id=0):
    CITIES_URL = f"https://api-sonuc.oyveotesi.org/api/v1/cities"
    DISTRICTS_URL = f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city_id}/districts"
    NEIGHBORHOODS_URL = f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city_id}/districts/{district_id}/neighborhoods"
    SCHOOLS_URL = f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city_id}/districts/{district_id}/neighborhoods/{neighborhood_id}/schools"
    SANDIKS_URL = f"https://api-sonuc.oyveotesi.org/api/v1/submission/school/{school_id}"

    if type == AreaType.CITY:
        url = CITIES_URL
    elif type == AreaType.DISTRICT:
        url = DISTRICTS_URL
    elif type == AreaType.NEIGHBORHOOD:
        url = NEIGHBORHOODS_URL
    elif type == AreaType.SCHOOL:
        url = SCHOOLS_URL
    elif type == AreaType.SANDIK:
        url = SANDIKS_URL
    else:
        print("Error: type is not valid")
        exit(1)

    try:
        time.sleep(SLEEP_TIME)
        print(f"Sending request to {url}")
        response = requests.get(
            url=url,
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.json()
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        return []


def gather_all():
    cities = get_cities()
    print_cities(cities)
    print("Gathered all cities")

def print_cities(cities):
    cities_dict = [city.to_dict() for city in cities]

    with open("tree.json", "w", encoding="utf-8") as f:
        json.dump(cities_dict, f, ensure_ascii=False, indent=4)


def get_cities():
    with open("cities.json", "r", encoding="utf-8") as f:
        cities_json = json.load(f)

    cities = [City(id=city["id"], name=city["name"], plate=city["plate"]) for city in cities_json]

    return cities

if __name__ == "__main__":
    with open("cities.json", "r", encoding="utf-8") as f:
        cities_json = json.load(f)
    
    city_plate = int(input("Enter city plate: "))

    city = None
    for city_json in cities_json:
        if city_json["plate"] == city_plate:
            city = City(id=city_json["id"], name=city_json["name"], plate=city_json["plate"])
            break

    if city is None:
        print("Error: city not found")
        exit(1)

    filename = f"{city.name}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(city.to_dict(), f, ensure_ascii=False, indent=4)
    print(f"Wrote to {filename}")

    print(f"Gathered city {city.name}")

    
        
