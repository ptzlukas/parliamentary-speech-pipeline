import pandas as pd
import re
import argparse
from tqdm import tqdm

def speeches_separation(input_file, output_file):
    # Step 1: Load the CSV file
    df = pd.read_csv(input_file)
    if 'text' not in df.columns:
        raise ValueError("The CSV file must contain a column named 'text'.")

    print(f"--- Step 1: Loaded CSV file with {len(df)} rows ---")

    # Step 2: Remove duplicate rows
    df = df.drop_duplicates()
    print(f"--- Step 2: Removed duplicates. Remaining rows: {len(df)} ---")

    # Step 3: Split text using regex patterns
    regex_list = [
        r"\s*(?:Dr\.\s+)?([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)*(?:\s+[A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)*)*)\s*,\s*(Bundesminister|Bundesministerin|Bundeskanzler|Bundeskanzlerin)(?:\s+[a-zäöüßA-ZÄÖÜ\s]+)?:",
        r"\s*(Präsident|Präsidentin|Vizepräsident|Vizepräsidentin)\s+(?:Dr\.\s+)?([A-Za-zÄÖÜäöüß\-]+(?:\s+[A-Za-zÄÖÜäöüß\-]+)*):",
        r"\s*(?:Dr\.\s+)?([A-Za-zÄÖÜäöüß\-]+\s+[A-Za-zÄÖÜäöüß\-]+(?:\s+[A-Za-zÄÖÜäöüß\-]+)*)\s+\(([A-ZÄÖÜß0-9\/\s\-]+|AfD)\):"
    ]

    regex_hits = {regex: 0 for regex in regex_list}
    new_rows = []

    # Iterate through rows to split text based on regex
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        text = row['text']
        other_data = row.drop('text')
        start_index = 0

        while start_index < len(text):
            next_match = None
            next_match_start = None
            next_match_end = None
            matched_regex = None

            for regex in regex_list:
                match = re.search(regex, text[start_index:])
                if match:
                    match_start_index = start_index + match.start()
                    match_end_index = start_index + match.end()

                    if next_match is None or match_start_index < next_match_start:
                        next_match = match
                        next_match_start = match_start_index
                        next_match_end = match_end_index
                        matched_regex = regex

            if next_match:
                regex_hits[matched_regex] += 1
                if start_index < next_match_start:
                    new_rows.append({**other_data, 'text': text[start_index:next_match_start].strip()})

                new_rows.append({**other_data, 'text': text[next_match_start:next_match_end].strip()})

                start_index = next_match_end
            else:
                new_rows.append({**other_data, 'text': text[start_index:].strip()})
                break

    print(f"--- Step 3: Split text. Total rows after splitting: {len(new_rows)} ---")
    for regex, count in regex_hits.items():
        print(f"Regex: {regex} - Matches: {count}")

    new_df = pd.DataFrame(new_rows)

    # Step 4: Extract additional fields (Speaker, Party, Dr., Title)
    new_df['Sprecher'] = None
    new_df['Partei'] = None
    new_df['Dr.'] = None
    new_df['Amt'] = None

    # Patterns for extraction
    patterns = [
        (r"\s*(?:Dr\.\s+)?([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)*(?:\s+[A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)*)*)\s*,\s*(Bundesminister|Bundesministerin|Bundeskanzler|Bundeskanzlerin)(?:\s+[a-zäöüßA-ZÄÖÜ\s]+)?:", 1),
        (r"\s*(Präsident|Präsidentin|Vizepräsident|Vizepräsidentin)\s+(?:Dr\.\s+)?([A-Za-zÄÖÜäöüß\-]+(?:\s+[A-Za-zÄÖÜäöüß\-]+)*):", 2),
        (r"\s*(?:Dr\.\s+)?([A-Za-zÄÖÜäöüß\-]+\s+[A-Za-zÄÖÜäöüß\-]+(?:\s+[A-Za-zÄÖÜäöüß\-]+)*)\s+\(([A-ZÄÖÜß0-9\/\s\-]+|AfD)\):", 3)
    ]

    rows_to_remove = []

    # Extract fields based on regex patterns
    for index, row in new_df.iterrows():
        text = row['text']
        if not isinstance(text, str) or text.strip().lower() in ["nan", "none", ""]:
            continue

        # Muster prüfen
        for pattern, pattern_type in patterns:
            match = re.match(pattern, text)
            if match:

                # Verarbeitung je nach Pattern
                if pattern_type == 1:
                    # Sprecher und Titel extrahieren
                    new_df.loc[index + 1, 'Sprecher'] = match.group(1)
                    new_df.loc[index + 1, 'Amt'] = match.group(2)
                    new_df.loc[index + 1, 'Dr.'] = "Dr." if "Dr." in text else None

                elif pattern_type == 2:
                    # Amt und Sprecher extrahieren
                    new_df.loc[index + 1, 'Amt'] = match.group(1)
                    new_df.loc[index + 1, 'Sprecher'] = match.group(2)
                    new_df.loc[index + 1, 'Dr.'] = "Dr." if "Dr." in text else None

                elif pattern_type == 3:
                    # Sprecher und Partei extrahieren
                    new_df.loc[index + 1, 'Sprecher'] = match.group(1)
                    new_df.loc[index + 1, 'Partei'] = match.group(2)
                    new_df.loc[index + 1, 'Dr.'] = "Dr." if "Dr." in text else None

                # Zeile zum Entfernen markieren
                rows_to_remove.append(index)
                break

    # Remove rows marked for deletion
    new_df = new_df.drop(index=rows_to_remove).reset_index(drop=True)

    print(f"--- Step 4: Extracted fields. Remaining rows: {len(new_df)} ---")

    # Step 5: Remove irrelevant rows
    new_df = new_df[~new_df['Amt'].isin(['Präsident', 'Präsidentin', 'Vizepräsident', 'Vizepräsidentin'])]
    new_df = new_df[new_df['Sprecher'].notna() & (new_df['Sprecher'] != '')]

    print(f"--- Step 5: Removed irrelevant rows. Remaining rows: {len(new_df)} ---")

    # Step 6: Merge speeches by the same speaker
    merged_rows = []
    current_row = None
    for _, row in new_df.iterrows():
        if current_row is None:
            current_row = row
        else:
            if row['Sprecher'] == current_row['Sprecher']:
                current_row['text'] = f"{current_row['text']} {row['text']}".strip()
            else:
                merged_rows.append(current_row)
                current_row = row

    if current_row is not None:
        merged_rows.append(current_row)

    merged_df = pd.DataFrame(merged_rows)

    print(f"--- Step 6: Merged speeches. Remaining rows: {len(merged_df)} ---")

    # Step 7: Remove text in parentheses
    merged_df['text'] = merged_df['text'].apply(lambda x: re.sub(r'\([^)]*\)', '', str(x)) if isinstance(x, str) else x)

    print(f"--- Step 7: Removed text in parentheses. ---")

    # Step 8: Add word count and filter short speeches
    merged_df['wordcount'] = merged_df['text'].str.split().apply(len)
    merged_df = merged_df[merged_df['wordcount'] > 200]

    print(f"--- Step 8: Filtered short speeches. Remaining rows: {len(merged_df)} ---")
    #Step 9:

    merged_rows = []
    current_row = None
    for _, row in merged_df.iterrows():
        if current_row is None:
            current_row = row
        else:
            if row['Sprecher'] == current_row['Sprecher']:
                current_row['text'] = f"{current_row['text']} {row['text']}".strip()
            else:
                merged_rows.append(current_row)
                current_row = row

    # Die letzte Zeile hinzufügen
    if current_row is not None:
        merged_rows.append(current_row)

    merged_df = pd.DataFrame(merged_rows)
    
    # Step 10: Save final result to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"--- Step 9: Saved processed speeches to {output_file} ---")

def main():
    parser = argparse.ArgumentParser(description="Process speeches from a CSV file.")
    parser.add_argument("--input-file", type=str, required=True, help="Input CSV file containing plenary protocols.")
    parser.add_argument("--output-file", type=str, default="processed_speeches.csv", help="Output CSV file name.")

    args = parser.parse_args()
    speeches_separation(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
