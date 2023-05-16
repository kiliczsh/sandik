import json
import os
import time

import tutanak


def extract_school_ids(data) -> list[str]:
    school_ids = []

    for district in data["districts"]:
        for neighborhood in district["neighborhoods"]:
            for school in neighborhood["schools"]:
                school_ids.append(school["id"])

    return school_ids


if __name__ == "__main__":
    city_json_path = input("Enter city json path: ")
    with open(city_json_path, "r", encoding="utf-8") as f:
        city_json = json.load(f)

    output_path = os.path.join("data", str(city_json["plate"]))

    os.makedirs(output_path, exist_ok=True)

    schools = extract_school_ids(city_json)

    for school in schools:
        result = tutanak.send_request(school)
        filename = os.path.join(output_path, f"school_{school}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
