import re
import csv

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
            csv_start_index = i
            break

    if csv_start_index is None:
        raise ValueError("Could not find CSV-like data in the HTML file.")

    csv_lines = lines[csv_start_index:]

    # Clean and write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for line in csv_lines:
            cleaned_line = line.lstrip('\ufeff \t')
            row = next(csv.reader([cleaned_line]))
            writer.writerow(row)

    print(f"✅ CSV data extracted and saved to: {output_csv_path}")


# Example usage:
extract_csv_from_html('./data/export_pedidos_2025-06-15.csv', './output/output.csv')