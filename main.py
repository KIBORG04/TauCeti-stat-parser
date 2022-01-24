import csv
import datetime

import requests

now = datetime.datetime.now()

FIELDS = ['date']
EXCLUDE_FIELDS = ['completion_html', "completion_antagonists", "content", "centcomm_communications"]

all_info = []

month = 8
day = 14
year = 2021

end_month = now.month
end_day = now.day
end_year = now.year


def build_url(_round, only_date):
    main_part = 'https://stat.taucetistation.org/json/'

    _year = str(year) + '/'

    _month = str(month)
    if month < 10:
        _month = '0' + str(month)
    _month += '/'

    _day = str(day)
    if day < 10:
        _day = '0' + str(day)
    _day += '/'

    if only_date:
        return main_part + _year + _month + _day

    round = str(_round) + '/'

    end = "stat.json"

    return main_part + _year + _month + _day + round + end


def recursion_write_info(_dict):
    parsed_info = {'date': "{}.{}.{}".format(day, month, 2021)}
    for field in _dict:
        if field in EXCLUDE_FIELDS:
            continue
        if type(_dict[field]) is dict:
            parsed_info.update(recursion_write_info(_dict[field]))
            continue
        if type(_dict[field]) is list:
            for inner_dict in _dict[field]:
                if type(inner_dict) is str:
                    if field not in FIELDS:
                        FIELDS.append(field)
                    parsed_info[field] = inner_dict
                    continue
                parsed_info.update(recursion_write_info(inner_dict))
                continue
            continue
        parsed_info[field] = _dict[field]
        if field not in FIELDS:
            FIELDS.append(field)
    return parsed_info


def write_info(page):
    all_json = page.json()

    parsed_info = recursion_write_info(all_json)

    all_info.append(parsed_info)


def write_in_csv():
    with open("ss-stats.csv", 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=FIELDS)

        writer.writeheader()
        for info in all_info:
            writer.writerow(info)


def get_round_ids(url):
    page = requests.get(url)
    if page.status_code == 404:
        return 404
    json_on_page = page.json()

    all_ids = []
    for dict in json_on_page:
        all_ids.append(dict["name"])

    return all_ids


if __name__ == '__main__':
    while month != end_month or day != end_day or year != end_year:
        url = build_url(1, True)
        rounds_on_page = get_round_ids(url)
        if rounds_on_page == 404:
            print("404 Error:" + url)
            if day == 31:
                day = 1
                month += 1
            else:
                day += 1

            if month == 12 and day == 31:
                year += 1
                day = 1
                month = 1
            continue
        index = 1
        for round in rounds_on_page:
            url = build_url(round, False)
            page = requests.get(url)
            print("parsed:" + url)
            write_info(page)
            if index == len(rounds_on_page):
                if day == 31:
                    day = 1
                    month += 1
                else:
                    day += 1

                if month == 12 and day == 31:
                    year += 1
                    day = 1
                    month = 1
            index += 1

    write_in_csv()
