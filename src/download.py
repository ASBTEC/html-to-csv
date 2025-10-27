#!/usr/bin/env python3
import argparse
import io
import json
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

def find_latest_file_in_folder(service, folder_id: str, filename: str):
    # Search by exact name inside the folder. If multiple, pick newest.
    query = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
    resp = service.files().list(
        q=query,
        fields="files(id, name, mimeType, createdTime)",
        orderBy="createdTime desc",
        pageSize=1,
    ).execute()
    files = resp.get("files", [])
    return files[0] if files else None

def download_file(service, file_id: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request, chunksize=8 * 1024 * 1024)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # You can print progress if desired: print(f"Download {int(status.progress()*100)}%")
    with open(out_path, "wb") as f:
        f.write(fh.getvalue())
    return str(out_path)

def main():
    parser = argparse.ArgumentParser(description="Download a Google Drive file by name from a specific folder.")
    parser.add_argument("-o", "--output", required=True, help="Output path (e.g. ./data/yourfile.xlsx)")
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    filename = output_path.name

    folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not folder_id:
        die("Missing env var DRIVE_FOLDER_ID (the Google Drive folder that stores Form uploads).")

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path:
        die("Missing env var GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON).")

    service = build_drive_service(creds_path)
    file_meta = find_latest_file_in_folder(service, folder_id, filename)
    if not file_meta:
        die(f"File named '{filename}' not found in folder {folder_id}.")

    saved = download_file(service, file_meta["id"], output_path)
    print(f"Downloaded to: {saved}")

if __name__ == "__main__":
    main()
