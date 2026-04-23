"""
sync_to_osf.py

Syncs key project files to OSF storage via the OSF WaterButler API.
Called automatically by the git post-push hook after every git push.

Skips: venv/, raw_data/, .git/, __pycache__/
(raw_data is too large; full repo is on GitHub at
 github.com/danielwaltersjdm/ears-dictionary-expansion)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

OSF_TOKEN = os.environ.get("OSF_TOKEN", "")
NODE_ID   = "bc9u5"
FILES_API = f"https://files.osf.io/v1/resources/{NODE_ID}/providers/osfstorage"
META_API  = f"https://api.osf.io/v2/nodes/{NODE_ID}/files/osfstorage"

EXCLUDE_DIRS = {"venv", "raw_data", ".git", "__pycache__", ".ipynb_checkpoints"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo"}
MAX_FILE_MB = 50
PROJECT_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def curl(*args) -> tuple[int, str]:
    """Run a curl command, return (http_code, body)."""
    result = subprocess.run(
        ["curl", "-s", "--insecure", *args],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout


def osf_list(path_id: str, token: str) -> list[dict]:
    """List all contents of an OSF storage folder, following pagination."""
    url = f"{META_API}/{path_id}/" if path_id else f"{META_API}/"
    items = []
    while url:
        _, body = curl("-H", f"Authorization: Bearer {token}", url)
        try:
            data = json.loads(body)
            items.extend(data.get("data", []))
            url = data.get("links", {}).get("next")  # follow next page
        except Exception:
            break
    return items


def osf_create_folder(parent_osf_path: str, name: str, token: str) -> str | None:
    """
    Create a folder named `name` inside parent_osf_path.
    parent_osf_path is like '/abc123/' or '' for root.
    Returns the new folder's OSF path (e.g. '/def456/'), or None on failure.
    """
    url = f"{FILES_API}{parent_osf_path}?kind=folder&name={name}"
    _, body = curl(
        "-X", "PUT",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Length: 0",
        url
    )
    try:
        data = json.loads(body)
        path = data["data"]["attributes"]["path"]
        return path  # e.g. '/69cff5e586a239d2c67f6d2b/'
    except Exception:
        return None


def osf_upload_file(osf_folder_path: str, name: str, local_path: Path, token: str) -> bool:
    """
    Upload a file into an OSF folder. osf_folder_path is like '/abc123/' or '/'.
    On 409 (file exists), parses the update URL from the response and retries.
    """
    url = f"{FILES_API}{osf_folder_path}?kind=file&name={name}"
    _, body = curl(
        "-X", "PUT",
        "-H", f"Authorization: Bearer {token}",
        "--data-binary", f"@{local_path}",
        "-w", "\n%{http_code}",
        url
    )
    lines = body.strip().splitlines()
    code = lines[-1] if lines else ""

    if code in ("200", "201"):
        return True

    # 409 = file already exists; the response body contains the update URL
    if code == "409":
        try:
            data = json.loads("\n".join(lines[:-1]))
            update_url = data["data"]["links"]["upload"]
            _, body2 = curl(
                "-X", "PUT",
                "-H", f"Authorization: Bearer {token}",
                "--data-binary", f"@{local_path}",
                "-w", "\n%{http_code}",
                update_url
            )
            lines2 = body2.strip().splitlines()
            return lines2[-1] in ("200", "201")
        except Exception:
            return False

    return False


def should_sync(rel: Path) -> bool:
    for part in rel.parts:
        if part in EXCLUDE_DIRS:
            return False
    if rel.suffix in EXCLUDE_EXTENSIONS:
        return False
    if (PROJECT_ROOT / rel).stat().st_size > MAX_FILE_MB * 1024 * 1024:
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token = OSF_TOKEN
    if not token:
        print("OSF_TOKEN not set - skipping OSF sync.")
        sys.exit(0)

    if NODE_ID == "PENDING":
        print("NODE_ID not set in sync_to_osf.py - skipping OSF sync.")
        sys.exit(0)

    # Collect files to sync
    files = [
        p.relative_to(PROJECT_ROOT)
        for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and should_sync(p.relative_to(PROJECT_ROOT))
    ]
    print(f"Syncing {len(files)} files to https://osf.io/{NODE_ID}/")

    # Build a map of existing OSF folders: posix_path -> osf_path_id
    folder_map: dict[str, str] = {"": "/"}

    def ensure_folder(posix: str) -> str | None:
        """Ensure folder exists, return its OSF path."""
        if posix in folder_map:
            return folder_map[posix]

        parts = posix.split("/")
        parent_posix = "/".join(parts[:-1])
        parent_osf = ensure_folder(parent_posix) if parent_posix else "/"
        if parent_osf is None:
            return None

        parent_id = parent_osf.strip("/")
        items = osf_list(parent_id, token)
        for item in items:
            attrs = item.get("attributes", {})
            if attrs.get("kind") == "folder" and attrs.get("name") == parts[-1]:
                osf_path = attrs["path"]
                folder_map[posix] = osf_path
                return osf_path

        parent_path = parent_osf if parent_osf != "/" else "/"
        osf_path = osf_create_folder(parent_path, parts[-1], token)
        if osf_path:
            folder_map[posix] = osf_path
        return osf_path

    ok, failed = 0, []
    for rel in files:
        parent_posix = rel.parent.as_posix() if rel.parent != Path(".") else ""
        osf_folder = ensure_folder(parent_posix) if parent_posix else "/"
        if osf_folder is None:
            failed.append(str(rel))
            continue
        if osf_upload_file(osf_folder, rel.name, PROJECT_ROOT / rel, token):
            ok += 1
            print(f"  OK  {rel.as_posix()}")
        else:
            failed.append(rel.as_posix())
            print(f"  FAIL {rel.as_posix()}")

    print(f"\nDone: {ok} uploaded, {len(failed)} failed")
    if failed:
        for name in failed:
            print(f"  FAILED: {name}")


if __name__ == "__main__":
    main()
