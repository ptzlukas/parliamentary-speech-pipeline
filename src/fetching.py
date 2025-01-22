import requests
import datetime
import math
import csv
import argparse
import os

BASE_URL = "https://search.dip.bundestag.de/api/v1/plenarprotokoll-text"
API_KEY = "I9FKdCn.hbfefNWCY336dL6x62vfwNKpoN2RZ1gp21"

def fetch_protokolle_for_date_range(start_date, end_date):
    data_list = []
    page = 0
    size = 40

    while True:
        params = {
            "f.datum.start": start_date,
            "f.datum.end": end_date,
            "format": "json",
            "apikey": API_KEY,
            "page": page,
            "size": size,
            "sort": "fundstelle.datum asc"
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        documents = data.get("documents", [])
        if not documents:
            break

        for document in documents:
            id_ = document.get("id")
            document_number = document.get("dokumentnummer")
            date = document.get("fundstelle", {}).get("datum")
            text = document.get("text")

            if id_ and document_number and date and text:
                text = text.replace("\n", " ").replace("\r", " ").strip()
                data_list.append({
                    "id": id_,
                    "dokumentnummer": document_number,
                    "datum": date,
                    "text": text
                })

        num_found = data.get("numFound", 0)
        total_pages = math.ceil(num_found / size)
        if page >= total_pages - 1:
            break

        page += 1

    return data_list

def fetch_all_protokolle(start_date, end_date):
    all_data = []
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current < end:
        next_month = (current + datetime.timedelta(days=31)).replace(day=1)
        current_end_date = min(next_month, end).strftime("%Y-%m-%d")

        print(f"Fetching protocols from {current.strftime('%Y-%m-%d')} to {current_end_date}...")
        data = fetch_protokolle_for_date_range(current.strftime("%Y-%m-%d"), current_end_date)
        all_data.extend(data)

        current = next_month

    return all_data

def save_to_csv(data_list, filename):
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(filename, mode="w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["id", "dokumentnummer", "datum", "text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data_list)

def main():
    parser = argparse.ArgumentParser(description="Fetch plenary protocols and save them to a CSV file.")
    parser.add_argument("--start-date", type=str, default="2019-09-10", help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", type=str, default="2024-10-18", help="End date in YYYY-MM-DD format.")
    parser.add_argument("--output-file", type=str, default="data/plenarprotokolle.csv", help="Output CSV file name.")
    
    args = parser.parse_args()

    protokolle = fetch_all_protokolle(args.start_date, args.end_date)
    save_to_csv(protokolle, args.output_file)
    print(f"--- Plenary protocols saved to {args.output_file} ---")

if __name__ == "__main__":
    main()
