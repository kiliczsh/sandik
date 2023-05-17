from dataclasses import dataclass
from enum import Enum
import json
import time
import requests
from dataclasses import dataclass
from typing import Dict


SLEEP_TIME = 1


@dataclass
class CMResultClass:
    image_url: str
    submission_id: int
    total_vote: int
    votes: Dict[str, int]


@dataclass
class ResultElement:
    ballot_box_number: int
    cm_result: CMResultClass
    mv_result: CMResultClass
    school_name: str


def send_request(school_id):
    SANDIKS_URL = f"https://api-sonuc.oyveotesi.org/api/v1/submission/school/{school_id}"

    try:
        time.sleep(SLEEP_TIME)
        print(f"Sending request to {SANDIKS_URL}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0"}
        response = requests.get(url=SANDIKS_URL, headers=headers)
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.json()
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        return []
    
if __name__ == "__main__":
    school_id = int(input("Enter school id: "))
    result = send_request(school_id)
    filename = f"school_{school_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


