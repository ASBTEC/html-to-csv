import re
import csv
import os

# This is my first vibe-coded piece of code. I asked chatGPT and I did not need to make any
# modifications. Nice!


def extract_csv_from_html(html_path, output_csv_path):
    with open(html_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Try to find the first line that looks like CSV headers
    lines = content.splitlines()
    csv_start_index = None

    for i, line in enumerate(lines):
        stripped = line.lstrip('\ufeff \t')
        if re.match(r'^"(?:[^"]|"")+",', stripped):
            print(f"match in {stripped}")
            csv_start_index = i
            break

    if csv_start_index is None:
        raise ValueError(f"Could not find CSV-like data in the HTML file {html_path}")

    csv_lines = lines[csv_start_index:]

    # Clean and write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for line in csv_lines:
            cleaned_line = line.lstrip('\ufeff \t')
            row = next(csv.reader([cleaned_line]))
            writer.writerow(row)

    print(f"CSV data extracted and saved to: {output_csv_path}")


input_dir = "./data"
output_dir = "./output"

for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)

    if os.path.basename(filename).__eq__(".gitignore"):  # Skip gitignores
        continue
    # Only process files (skip subfolders)
    if os.path.isfile(input_path):
        output_path = os.path.join(output_dir, filename)
        extract_csv_from_html(input_path, output_path)
        print(f"Processed {filename} → {output_path}")