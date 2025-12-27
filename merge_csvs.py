import pandas as pd
import glob
import os
import re

def normalize_columns(df):
    df.columns = [
        re.sub(r'[^a-z0-9_]', '',
               col.strip().lower().replace(" ", "_"))
        for col in df.columns
    ]
    return df

def merge_csvs(input_folder, output_file):
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    if not csv_files:
        print("❌ No CSV files found")
        return

    dataframes = []

    for file in csv_files:
        print(f"Reading: {os.path.basename(file)}")
        try:
            df = pd.read_csv(
                file,
                sep=None,
                engine="python",
                on_bad_lines="skip",
                encoding_errors="ignore"
            )

            df = normalize_columns(df)
            df["source_file"] = os.path.basename(file)

            dataframes.append(df)

        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

    if not dataframes:
        print("❌ No valid CSV data found")
        return

    # 🔹 Merge all
    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

    # 🔹 Remove FULL duplicate rows
    before = len(merged_df)
    merged_df.drop_duplicates(inplace=True)
    after = len(merged_df)

    print(f"🧹 Removed {before - after} duplicate rows")

    # 🔹 OPTIONAL: Key-based deduplication
    possible_keys = [col for col in merged_df.columns
                     if col in ["email", "phone", "mobile", "contact", "phone_no"]]

    if possible_keys:
        merged_df.drop_duplicates(subset=possible_keys, inplace=True)
        print(f"🔑 Deduplicated using keys: {possible_keys}")

    merged_df.to_csv(output_file, index=False)
    print(f"\n✅ Final merged file saved as: {output_file}")
    print(f"📊 Total rows: {len(merged_df)}")

if __name__ == "__main__":
    merge_csvs("input_csvs", "merged_output.csv")
