import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def evaluate_dataset(input_file, output_folder):
    # Step 1: Load the dataset
    df = pd.read_csv(input_file)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 2: Wordcount histogram
    print("--- Step 2: Generating Wordcount Histogram ---")
    if 'speech' not in df.columns:
        raise ValueError("The column 'speech' is missing from the dataset.")

    df['wordcount'] = df['speech'].str.split().apply(len)
    plt.figure(figsize=(10, 6))
    plt.hist(df['wordcount'], bins=50, color='skyblue', edgecolor='black')
    plt.xlabel('Wordcount')
    plt.ylabel('Frequency')
    plt.title('Distribution of Wordcount')
    plt.xlim(200, 3500)
    plt.grid(True)
    plt.savefig(os.path.join(output_folder, 'wordcount_histogram.png'))
    plt.close()

    # Step 3: Unique values in categorical columns
    print("--- Step 3: Analyzing Unique Values ---")
    unique_values_report = {}
    for column in ['speaker', 'party', 'position']:
        if column in df.columns:
            unique_values = df[column].nunique()
            unique_values_report[column] = unique_values

        # Step 4: Statistical Summary
    print("--- Step 4: Generating Statistical Summary ---")
    stats = df[['wordcount']].describe()

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 5: Save results to file
    report_path = os.path.join(output_folder, 'evaluation_report.txt')
    with open(report_path, 'w') as f:
        f.write("=== Evaluation Report ===\n")
        
        # Write unique values report
        f.write("\n--- Unique Values ---\n")
        for column, unique_count in unique_values_report.items():
            if column == 'speaker':  # Skip 'speaker' column
                f.write(f"{column}: Skipped reporting unique values, because list is too long.\n")
                continue
            else:
                unique_values = df[column].unique()  # Get the unique values
                f.write(f"{column}: {unique_count} unique values ({', '.join(map(str, unique_values))})\n")
        
        # Write statistical summary
        f.write("\n--- Statistical Summary ---\n")
        f.write(stats.to_string())

    print(f"--- Evaluation completed. Report saved to {report_path} ---")

    # Step 6: Save processed dataset with wordcount
    final_output_path = os.path.join(output_folder, 'final_processed_dataset.csv')
    df.to_csv(final_output_path, index=False)
    print(f"--- Final processed dataset saved to {final_output_path} ---")

def main():
    parser = argparse.ArgumentParser(description="Evaluate the final dataset and generate reports.")
    parser.add_argument("--input-file", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output-folder", type=str, default="data/evaluation", help="Folder to save evaluation outputs.")
    args = parser.parse_args()

    evaluate_dataset(args.input_file, args.output_folder)

if __name__ == "__main__":
    main()
