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

def extract_file_id_from_url(url: str) -> str:
    s = str(url or "")
    # /file/d/<id>/
    import re
    m = re.search(r"/file/d/([a-zA-Z0-9_-]{10,})/", s)
    if m:
        return m.group(1)
    # ...?id=<id>
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]{10,})", s)
    if m:
        return m.group(1)
    # uc?id=<id>
    m = re.search(r"uc\?id=([a-zA-Z0-9_-]{10,})", s)
    if m:
        return m.group(1)
    # As a last resort, assume the whole thing is already an ID
    if s and all(c.isalnum() or c in "-_" for c in s) and len(s) >= 10:
        return s
    die("Could not extract a Drive file ID from the provided URL/ID.")

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
        status, done = downloader.next_chunk()
        # Optional: print progress here
    with open(out_path, "wb") as f:
        f.write(fh.getvalue())
    print(f"Downloaded to: {out_path}")
    return str(out_path)

def main():
    parser = argparse.ArgumentParser(
        description="Download a Google Drive file by URL (or ID) using a service account."
    )
    parser.add_argument("-u", "--url", required=True, help="Google Drive file URL (or raw file ID)")
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output directory or file path. If a directory, the Drive file name is used."
    )
    args = parser.parse_args()

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path:
        die("Missing env var GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON).")

    service = build_drive_service(creds_path)
    file_id = extract_file_id_from_url(args.url)

    out = Path(args.output).resolve()
    if out.exists() and out.is_dir():
        # If output is an existing dir, use Drive filename inside it
        filename = fetch_file_name(service, file_id)
        out_path = out / filename
    else:
        # If output looks like a file path (possibly in a non-existing dir), respect it
        # If it ends with a path separator or doesn't have a suffix but you intended a dir,
        # just create that dir beforehand.
        if str(args.output).endswith(("/", "\\")):
            die("Output points to a directory path that doesn't exist. Create it first or pass a file path.")
        out_path = out

    download_file(service, file_id, out_path)

if __name__ == "__main__":
    main()
