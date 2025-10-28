#!/usr/bin/env python3
import argparse
import io
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def build_drive_service(creds_path: str):
    if not os.path.exists(creds_path):
        die(f"GOOGLE_APPLICATION_CREDENTIALS file not found: {creds_path}")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build("drive", "v3", credentials=credentials, cache_discovery=False)

def fetch_file_name(service, file_id: str) -> str:
    meta = service.files().get(fileId=file_id, fields="id,name").execute()
    name = meta.get("name")
    if not name:
        die("Unable to fetch file name from Drive metadata.")
    return name

def download_file(service, file_id: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request, chunksize=8 * 1024 * 1024)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    with open(out_path, "wb") as f:
        f.write(fh.getvalue())
    print(f"Downloaded to: {out_path}")
    return str(out_path)

def main():
    parser = argparse.ArgumentParser(
        description="Download a Google Drive file by ID using a service account."
    )
    parser.add_argument("-i", "--id", required=True, help="Google Drive file ID (e.g. 1CZgZi...)")
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output directory or file path. If a directory, the Drive file name is used."
    )
    args = parser.parse_args()

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path:
        die("Missing env var GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON).")

    service = build_drive_service(creds_path)
    file_id = args.id

    out = Path(args.output).resolve()
    if out.exists() and out.is_dir():
        # If output is an existing dir, use Drive filename inside it
        filename = fetch_file_name(service, file_id)
        out_path = out / filename
    else:
        if str(args.output).endswith(("/", "\\")):
            die("Output points to a directory path that doesn't exist. Create it first or pass a file path.")
        out_path = out

    download_file(service, file_id, out_path)


if __name__ == "__main__":
    main()
