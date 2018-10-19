#!/usr/bin/env python3
import argparse
import datetime
import requests
from typing import List


def get_token():
    with open("token.key") as f:
        return f.readline()


API_URL = 'https://api.fib.upc.edu/v2/'
TOKEN = get_token()


def time_to_int(time: str) -> int:
    h, m = time.split(":")
    return int(h)*60 + int(m)


def build_database(data: dict) -> dict:
    total = {}
    for d in data:
        # code = f"{d['codi_assig']}-{d['tipus']}"
        code = d['codi_assig']
        groups = total.get(code, {})

        t_start = time_to_int(d["inici"])
        t_end = t_start + int(d["durada"])*60

        groups[int(d["grup"])] = {
            "start": t_start,
            "end": t_end,
            # "type": d["tipus"],
            # "aula": d["aules"]
        }

        total[code] = groups
    return total


def get_timetable(year: int, semester: int, courses: List[str]):
    date_str = f"{year}Q{semester}"
    res = requests.get(f"{API_URL}quadrimestres/{date_str}/classes/",
                       params={
                           "format": "json",
                           "codi_assig": courses,
                           "client_id": TOKEN
                       })
    print(res.request.path_url)
    data = res.json()
    if data["count"] <= 0:
        print(f"No data received, instead {data}")

    database = build_database(data["results"])
    print(database)


def get_available_courses(year: int, semester: int) -> List[str]:
    date_str = f"{year}Q{semester}"
    res = requests.get(f"{API_URL}quadrimestres/{date_str}/assignatures",
                       params={
                           "format": "json",
                           "client_id": TOKEN
                       })
    print(res.request.path_url)
    return res.json()["results"]


def main(args: dict):
    get_timetable(2018, 1, ["F", "FM", "IC", "PRO1"])
    get_available_courses(2018, 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    arguments, _ = parser.parse_known_args()
    main(vars(arguments))

