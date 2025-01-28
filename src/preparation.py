import pandas as pd
import re
import argparse
import numpy as np

#id,dokumentnummer,datum,text,Sprecher,,wordcount

def preprocess_data(input_file, output_file):
    # Load CSV
    df = pd.read_csv(input_file)
    
    
    # Convert 'datum' column to standardized date format
    # df['datum'] = pd.to_datetime(df['datum'], format='%d.%m.%Y')
    # df['datum'] = df['datum'].dt.strftime('%Y-%m-%d')
    df = df.drop('wordcount', axis=1)

    df['datum'] = pd.to_datetime(df['datum'], format='%Y-%m-%d')
    df['Dr.'] = df['Dr.'].apply(lambda x: 1 if x == 'Dr.' else 0)
    df['Sprecher'] = df['Sprecher'].astype('str')

    # Remove duplicate texts
    df = df.drop_duplicates(subset='text', keep='first')

    # Filter parties
    filtered_parties = ['BSW', 'AfD', 'CDU/CSU', 'FDP', 'SPD', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN']
    df = df[df['Partei'].isin(filtered_parties) | df['Partei'].isna()]

    

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

    # Define roles that should not be replaced

    df['Amt'] = df['Amt'].fillna('Abgeordnete(r)')

    # Remove Bundesrat entries
    # Function to check if a value is a pure integer
    def is_int(x):
        try:
            int(x)
            return True
        except ValueError:
            return False

    df['is_bundestag'] = df['dokumentnummer'].apply(is_int)
    df = df[~df['is_bundestag']]  # Nur Einträge beibehalten, bei denen 'is_bundestag' True ist
    

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
    df = df[df['wordcount'] <= 3500]
    # Remove rows containing "Abgeordnet" in the speaker name
    
    #Until know there are some remaining problems with the regex pattern. When you search for protokolls further in past because protocol regulations have changed
    df = df[~df['Sprecher'].str.contains("Abgeordnet")]
    df = df[~df['Sprecher'].str.contains("die Frage")]
    df = df[~df['Sprecher'].str.contains("Zustimmung")]
    df = df[~df['Sprecher'].str.contains("Beifall")]

    # Add unique ID column
    df['u_id'] = range(1, len(df) + 1)

    df = df.drop('is_bundestag', axis=1)

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
