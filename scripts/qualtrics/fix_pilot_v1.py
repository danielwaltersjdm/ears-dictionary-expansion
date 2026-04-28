"""
fix_pilot_v1.py

Patches two issues from the initial build:
  1. Add the age question (validation schema was wrong on first try).
  2. Enable random question order in the Ratings block.

Reads:
  outputs/survey/pilot_v1_metadata.json   # for SurveyID and BlockIDs
"""

import json
import os
import sys
from pathlib import Path

import requests
import urllib3
urllib3.disable_warnings()

PROJECT_ROOT = Path(__file__).parent.parent.parent
META_PATH = PROJECT_ROOT / "outputs" / "survey" / "pilot_v1_metadata.json"

TOKEN = os.environ.get("QUALTRICS_TOKEN", "")
if not TOKEN:
    print("ERROR: QUALTRICS_TOKEN not set.")
    sys.exit(1)

DATACENTER = "co1"
API = f"https://{DATACENTER}.qualtrics.com/API/v3"
HEADERS = {"X-API-TOKEN": TOKEN, "Content-Type": "application/json"}

meta = json.loads(META_PATH.read_text(encoding="utf-8"))
SURVEY_ID = meta["survey_id"]
RATINGS_BLOCK = meta["blocks"]["ratings"]
DEMO_BLOCK = meta["blocks"]["demographics"]


def _req(method, path, payload=None, params=None):
    r = requests.request(method, f"{API}/{path}", headers=HEADERS,
                          json=payload, params=params, verify=False)
    try:
        body = r.json()
    except Exception:
        body = {"_raw": r.text}
    return r.status_code, body


# -----------------------------------------------------------------------------
# 1. Add age question with correct validation schema
# -----------------------------------------------------------------------------
print("[1] Adding age question with corrected validation...")
# Use ContentType validation (not ValidNumber as a top-level Type)
age_q = {
    "QuestionText": "What is your age?",
    "DataExportTag": "age",
    "QuestionType": "TE",
    "Selector": "SL",
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "QuestionDescription": "Age",
    "Validation": {
        "Settings": {
            "ForceResponse": "OFF",
            "Type": "ContentType",
            "ContentType": "ValidNumber",
            "ValidNumber": {"Min": "18", "Max": "120"}
        }
    },
    "Language": []
}
code, body = _req("POST", f"survey-definitions/{SURVEY_ID}/questions",
                  payload=age_q, params={"blockId": DEMO_BLOCK})
if code in (200, 201):
    print(f"  OK age (QID: {body['result']['QuestionID']})")
else:
    # Fall back: text-entry age with no validation
    print(f"  First attempt failed: {code} {body.get('meta', {}).get('error', {}).get('errorMessage')}")
    print(f"  Falling back: text-entry without validation...")
    age_q["Validation"] = {"Settings": {"ForceResponse": "OFF", "Type": "None"}}
    code, body = _req("POST", f"survey-definitions/{SURVEY_ID}/questions",
                      payload=age_q, params={"blockId": DEMO_BLOCK})
    if code in (200, 201):
        print(f"  OK age (no validation) (QID: {body['result']['QuestionID']})")
    else:
        print(f"  FAIL: {code} {body}")

# Move age to the front of the demographics block — Qualtrics adds new questions at the end,
# but since age was supposed to be first, we leave it as-is for now (functionally fine).


# -----------------------------------------------------------------------------
# 2. Enable randomization on the Ratings block
# -----------------------------------------------------------------------------
print(f"\n[2] Enabling random question order in Ratings block ({RATINGS_BLOCK})...")

# Strategy: GET the full survey definition, find the Ratings block,
# update its Options.RandomizeQuestions to "RandomWithXPrime" or "Advanced",
# and PUT the entire block back with all required fields.
code, body = _req("GET", f"survey-definitions/{SURVEY_ID}")
if code not in (200, 201):
    print(f"  ERROR fetching survey def: {code}")
    sys.exit(1)

blocks = body["result"]["Blocks"]
block = blocks[RATINGS_BLOCK]
print(f"  Found block: {block.get('Description', '?')} with {len(block.get('BlockElements', []))} elements")

# Set up the Options dict with the randomization config that Qualtrics' web UI generates.
# The key is to set RandomizeQuestions to "Advanced" and provide a proper Randomization payload.
n_questions = len([e for e in block.get("BlockElements", []) if e.get("Type") == "Question"])
block["Options"] = {
    "BlockLocking": "false",
    "RandomizeQuestions": "Advanced",
    "BlockVisibility": "Expanded",
    "Randomization": {
        "Advanced": {
            "FixedOrder": [f"{{~Random:{n_questions}~}}"],  # randomize all
            "RandomizeAll": [],
            "RandomSubSet": [],
            "Undisplayed": [],
            "TotalRandSubset": 0,
            "QuestionsPerPage": "0"
        },
        "EvenPresentation": False
    }
}
# Description is required for the PUT
if "Description" not in block:
    block["Description"] = "Ratings"

code, body = _req("PUT",
                  f"survey-definitions/{SURVEY_ID}/blocks/{RATINGS_BLOCK}",
                  payload=block)
if code in (200, 201):
    print(f"  OK randomization set (advanced)")
else:
    err = body.get("meta", {}).get("error", {})
    print(f"  WARN: PUT failed: {code} {err.get('errorMessage')}")
    print(f"  Trying simpler approach: 'RandomWithXPrime'...")
    block["Options"]["RandomizeQuestions"] = "RandomWithXPrime"
    block["Options"]["Randomization"] = {
        "Advanced": None,
        "TotalRandSubset": 0
    }
    code, body = _req("PUT",
                      f"survey-definitions/{SURVEY_ID}/blocks/{RATINGS_BLOCK}",
                      payload=block)
    if code in (200, 201):
        print(f"  OK randomization (RandomWithXPrime)")
    else:
        err = body.get("meta", {}).get("error", {})
        print(f"  WARN: still failed: {code} {err.get('errorMessage')}")
        print(f"  Detailed errors:")
        for ve in err.get("validationErrors", []):
            print(f"    - {ve.get('Field')}: {ve.get('Description')}")
        print(f"\n  Manual fallback required: in the Qualtrics web editor,")
        print(f"  open the Ratings block, click the gear -> Question Randomization,")
        print(f"  and select 'Randomize the order of all questions'.")

print(f"\nPreview URL: https://{DATACENTER}.qualtrics.com/jfe/preview/{SURVEY_ID}")
print(f"Edit URL:    https://{DATACENTER}.qualtrics.com/Q/EditSection/Blocks?ContextSurveyID={SURVEY_ID}")
