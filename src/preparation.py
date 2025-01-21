import pandas as pd
import re
import argparse

#id,dokumentnummer,datum,text,Sprecher,,wordcount

def preprocess_data(input_file, output_file):
    # Load CSV
    df = pd.read_csv(input_file)

    # Convert 'datum' column to standardized date format
    # df['datum'] = pd.to_datetime(df['datum'], format='%d.%m.%Y')
    # df['datum'] = df['datum'].dt.strftime('%Y-%m-%d')
    df = df.drop('wordcount', axis=1)

    df['datum'] = pd.to_datetime(df['datum'], format='%Y-%m-%d')

    # Convert 'Dr.' column to binary format
    df['Dr.'] = df['Dr.'].apply(lambda x: 1 if x == 'Dr.' else 0)

    # Convert columns to string
    df['Amt'] = df['Amt'].astype('str')
    df['Partei'] = df['Partei'].astype('str')
    df['Sprecher'] = df['Sprecher'].astype('str')

    # Remove duplicate texts
    df = df.drop_duplicates(subset='text', keep='first')

    # Regex to validate names
    name_pattern = r'^([A-ZÄÖÜ][a-zäöü]+(-[A-ZÄÖÜ][a-zäöü]+)*\s?)+,\s*([A-ZÄÖÜ][a-zäöü]+(-[A-ZÄÖÜ][a-zäöü]+)*)$'

    def ist_name(value):
        return bool(re.match(name_pattern, value))

    # Add a column to check for valid names
    df['ist_name'] = df['Sprecher'].apply(ist_name)

    # Filter parties
    filtered_parties = ['BSW', 'AfD', 'CDU/CSU', 'FDP', 'SPD', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN']
    df = df[df['Partei'].isin(filtered_parties) | df['Partei'].isnull()]

    # Dictionary to manually assign parties
    dic_sprecher_partei = {
        "Olaf Scholz": "SPD",
        "Peter Altmaier": "CDU/CSU",
        "Julia Klöckner": "CDU/CSU",
        "Angela Merkel": "CDU/CSU",
        "Heiko Maas": "SPD",
        "Annegret Kramp-Karrenbauer": "CDU/CSU",
        "Gerd Müller": "CDU/CSU",
        "Christine Lambrecht": "SPD",
        "Andreas Scheuer": "CDU/CSU",
        "Franziska Giffey": "SPD",
        "Anja Karliczek": "CDU/CSU",
        "Hubertus Heil": "SPD",
        "Jens Spahn": "CDU/CSU",
        "Helge Braun": "CDU/CSU",
        "Karl Lauterbach": "SPD",
        "Christian Lindner": "FDP",
        "Bettina Stark-Watzinger": "FDP",
        "Robert Habeck": "BÜNDNIS 90/DIE GRÜNEN",
        "Nancy Faeser": "SPD",
        "Marco Buschmann": "FDP",
        "Annalena Baerbock": "BÜNDNIS 90/DIE GRÜNEN",
        "Volker Wissing": "FDP",
        "Cem Özdemir": "BÜNDNIS 90/DIE GRÜNEN",
        "Svenja Schulze": "SPD",
        "Lisa Paus": "BÜNDNIS 90/DIE GRÜNEN",
        "Wolfgang Schmidt": "SPD",
        "Boris Pistorius": "SPD",
        "Klara Geywitz": "SPD",
    }

    # Assign missing Partei affiliations
    df_nan = df[df['Partei'].isna()]
    for index, row in df_nan.iterrows():
        sprecher = row['Sprecher']
        if sprecher in dic_sprecher_partei:
            df.loc[index, 'Partei'] = dic_sprecher_partei[sprecher]
        else:
            df.drop(index, inplace=True)

    # Fill missing roles with "Abgeordnete(r)"
    df['Amt'] = df['Amt'].replace('nan', pd.NA)
    df.loc[df['Amt'].isnull() | (df['Amt'] == ''), 'Amt'] = 'Abgeordnete(r)'

    # Remove Bundesrat entries
    def is_int(x):
        try:
            int(x)
            return True
        except ValueError:
            return False

    df['is_bundesrat'] = df['dokumentnummer'].apply(is_int)
    df = df[~df['is_bundesrat']]

    # Combine speeches split by interjections
    grouped_data = (
        df.groupby(['id', 'dokumentnummer', 'datum', 'Sprecher'], as_index=False)
        .agg({
            'id': 'first',
            'text': ' '.join,
            'Partei': 'first',
            'Dr.': 'first',
            'Amt': 'first',
        })
    )

    # Add word count
    def count_words(text):
        return len(text.split())

    df['wordcount'] = df['text'].apply(count_words)

    # Remove rows containing "Abgeordnet" in the speaker name
    df = df[~df['Sprecher'].str.contains("Abgeordnet")]

    # Add unique ID column
    df['u_id'] = range(1, len(df) + 1)

    df = df.drop('is_bundesrat', axis=1)
    df = df.drop('ist_name', axis=1)
    column_mapping = {
    "id": "session_id",
    "dokumentnummer": "document_id",
    "datum": "date",
    "text": "speech",
    "Sprecher": "speaker",
    "Partei": "party",
    "Dr.": "is_doctor",
    "Amt": "position",  
    }   

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Rearrange columns
    desired_order = [
        "u_id",
        "session_id",
        "document_id",
        "date",
        "is_doctor",
        "speaker",
        "party",
        "position",
        "speech",
    ]

    df = df[desired_order]


    # Reset index and save to CSV
    df = df.reset_index(drop=True)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Preprocessed data saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess a CSV file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    preprocess_data(args.input, args.output)
