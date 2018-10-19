#!/usr/bin/env python3
import argparse
import datetime
import requests
from typing import List, Tuple, Dict


def get_token():
    with open("token.key") as f:
        return f.readline()


API_URL = 'https://api.fib.upc.edu/v2/'
TOKEN = get_token()


def overlaps(ranges: List[Tuple[int, int]], new_ranges: List[Tuple[int, int]]) -> bool:
    for start, end in ranges:
        for n_start, n_end in new_ranges:
            if n_start < end or n_end > start:
                return True
    return False


def get_timetables(courses: dict, groups: dict, ranges: List[Tuple[int, int]]) -> List[Dict[str, int]]:
    for subject_key, subject_data in courses.items():
        courses_copy = courses.copy()
        del courses_copy[subject_key]
        for group_key, group_data in subject_data.items():
            if not overlaps(ranges, group_data["time"]):
                

            if len(group_data["subgroups"]) <= 0:
                pass



def time_to_int(time: str) -> int:
    h, m = time.split(":")
    return int(h)*60 + int(m)


def build_database(data: dict) -> Tuple[dict, dict]:
    subjects_data = {}
    # Parse the JSON file
    for d in data:
        code = d['codi_assig']
        groups = subjects_data.get(code, {})

        t_start = int(d["dia_setmana"])*60*24 + time_to_int(d["inici"])
        t_end = t_start + int(d["durada"])*60

        total_num = int(d["grup"])
        group_num = total_num // 10
        subgroup_num = total_num % 10
        group = groups.get(group_num, {
            "subgroups": {},
            "time": []
        })

        if total_num % 10 == 0:
            group["time"].append((t_start, t_end))
        else:
            subgroup = group["subgroups"].get(subgroup_num, [])
            subgroup.append((t_start, t_end))
            group["subgroups"][subgroup_num] = subgroup
        groups[group_num] = group
        subjects_data[code] = groups

    # Post process data and extract all the ids
    groups = {}
    for subject_key, subject_data in subjects_data.items():
        groups_ids = []
        for group_key, group_data in subject_data.items():
            if len(group_data["subgroups"]) > 0:
                groups_ids += [group_key*10 + key for key in group_data["subgroups"].keys()]
            else:
                groups_ids.append(group_key*10)
        groups[subject_key] = groups_ids
    return subjects_data, groups


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

