"""
build_pilot_v1.py

Build the EARS Pilot v1 survey on Qualtrics:
  - All 297 Loughran-McDonald Uncertainty words
  - Each word rated on TWO unipolar 7-point scales (Epistemic intensity, Aleatory intensity)
  - Within-subject (every subject rates every word)
  - Generic Tulane consent placeholder
  - Brief construct tutorial
  - Demographics + open feedback at end
  - Created in Inactive state (preview only)

Reads:
  outputs/loughran_mcdonald_uncertainty_297.csv

Writes:
  outputs/survey/pilot_v1_metadata.json   # survey ID + preview URLs
  outputs/survey/pilot_v1_build.log       # full build log

Auth:
  Reads QUALTRICS_TOKEN from environment.
  Datacenter is hard-coded to co1 per whoami response.
"""

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import urllib3
urllib3.disable_warnings()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent
WORDLIST_CSV = PROJECT_ROOT / "outputs" / "loughran_mcdonald_uncertainty_297.csv"
META_OUT     = PROJECT_ROOT / "outputs" / "survey" / "pilot_v1_metadata.json"
LOG_OUT      = PROJECT_ROOT / "outputs" / "survey" / "pilot_v1_build.log"

TOKEN = os.environ.get("QUALTRICS_TOKEN", "")
if not TOKEN:
    print("ERROR: QUALTRICS_TOKEN environment variable not set.")
    sys.exit(1)

DATACENTER = "co1"
API = f"https://{DATACENTER}.qualtrics.com/API/v3"
HEADERS = {"X-API-TOKEN": TOKEN, "Content-Type": "application/json"}

SURVEY_ID         = "SV_ahjVK84570ekXFY"
DEFAULT_BLOCK_ID  = "BL_4MXu5K97wFUxZ7o"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _req(method, path, payload=None, params=None):
    url = f"{API}/{path}"
    r = requests.request(
        method, url, headers=HEADERS, json=payload, params=params, verify=False
    )
    try:
        body = r.json()
    except Exception:
        body = {"_raw": r.text}
    return r.status_code, body


def post(path, payload=None, params=None):
    return _req("POST", path, payload, params)


def put(path, payload=None, params=None):
    return _req("PUT", path, payload, params)


def get(path, params=None):
    return _req("GET", path, None, params)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

def flush_log():
    LOG_OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Survey content templates
# ---------------------------------------------------------------------------

CONSENT_TEXT = """\
<h3>Consent to Participate</h3>
<p>You are being invited to participate in a research study examining how people
interpret words that signal uncertainty. The study is being conducted by
Daniel Walters, Ph.D., at the A.B. Freeman School of Business, Tulane University.</p>

<p><b>What you will be asked to do.</b> You will see 297 English words that have
been used to describe uncertainty in business and financial documents. For each
word, you will rate how well it conveys two distinct aspects of uncertainty
(epistemic and aleatory). The survey takes approximately 25-30 minutes.</p>

<p><b>Risks and benefits.</b> There are no known risks or direct benefits to you
beyond your compensation for participation.</p>

<p><b>Compensation.</b> [Compensation amount to be specified at deployment.]</p>

<p><b>Confidentiality.</b> Your responses are anonymous. We do not collect any
identifying information beyond basic demographics.</p>

<p><b>Voluntary participation.</b> Your participation is entirely voluntary. You
may stop at any time without penalty.</p>

<p><b>Contact.</b> Questions about this study can be directed to djw307@gmail.com.
Questions about your rights as a participant can be directed to the Tulane
Human Research Protection Office.</p>

<p><b>This is placeholder consent text. Replace with IRB-approved text before deployment.</b></p>
"""

INSTRUCTIONS_TEXT = """\
<h3>Instructions</h3>
<p>This study is about how people interpret words that signal <b>uncertainty</b>.
Researchers have argued that uncertainty comes in two distinct flavors:</p>

<p><b>Epistemic uncertainty</b> is uncertainty due to <em>missing information or
limited knowledge</em>. The outcome itself is, in principle, knowable -- you
just don't know it yet. Examples:</p>
<ul>
<li>"I'm not sure how many seeds are in this apple, but I could count them."</li>
<li>"I don't know who won the 1984 Cy Young Award, but I could look it up."</li>
</ul>

<p><b>Aleatory uncertainty</b> is uncertainty due to <em>inherent randomness or
variability</em>. The outcome is fundamentally unpredictable, even if you knew
everything relevant. Examples:</p>
<ul>
<li>"I don't know what a coin will land on -- even with perfect information about
the coin, the outcome is random."</li>
<li>"Stock returns fluctuate day-to-day in ways that depend on chance events."</li>
</ul>

<p>Some words signal one type more than the other; some signal both; some signal
neither. Your job is to rate each word on <b>two scales</b>:</p>

<ol>
<li>How strongly does this word convey <b>epistemic</b> uncertainty? (1-7)</li>
<li>How strongly does this word convey <b>aleatory</b> uncertainty? (1-7)</li>
</ol>

<p>If you are unfamiliar with a word, you may skip it.</p>

<p>Click the arrow below to begin.</p>
"""

# Word-rating question template
def word_question_payload(word, qid_text):
    """
    Returns a Matrix Likert question with two statements (epistemic, aleatory)
    rated on a 7-point scale.
    """
    return {
        "QuestionText": (
            f'<h3>{word}</h3>'
            f'<p>How strongly does the word "<b>{word}</b>" convey each kind of '
            f'uncertainty?</p>'
        ),
        "DataExportTag": qid_text,
        "QuestionType": "Matrix",
        "Selector": "Likert",
        "SubSelector": "SingleAnswer",
        "Configuration": {
            "QuestionDescriptionOption": "UseText",
            "TextPosition": "inline",
            "ChoiceColumnWidth": 25,
            "RepeatHeaders": "none",
            "WhiteSpace": "OFF",
            "MobileFirst": False
        },
        "QuestionDescription": f'Rate the word "{word}" on epistemic and aleatory dimensions.',
        "Choices": {
            "1": {"Display": "<b>Epistemic uncertainty</b><br/><i>(missing information / could be known)</i>"},
            "2": {"Display": "<b>Aleatory uncertainty</b><br/><i>(inherent randomness / chance)</i>"}
        },
        "ChoiceOrder": ["1", "2"],
        "Validation": {
            "Settings": {"ForceResponse": "OFF", "Type": "None"}
        },
        "Language": [],
        "Answers": {
            "1": {"Display": "1<br/>Not at all"},
            "2": {"Display": "2"},
            "3": {"Display": "3"},
            "4": {"Display": "4<br/>Moderately"},
            "5": {"Display": "5"},
            "6": {"Display": "6"},
            "7": {"Display": "7<br/>Very strongly"}
        },
        "AnswerOrder": ["1", "2", "3", "4", "5", "6", "7"]
    }


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------

def add_descriptive_text(block_id, qid_export, html, qid_description):
    """Add a Descriptive Text question to a block."""
    payload = {
        "QuestionText": html,
        "DataExportTag": qid_export,
        "QuestionType": "DB",
        "Selector": "TB",
        "Configuration": {
            "QuestionDescriptionOption": "SpecifyLabel",
            "LabelPosition": "BELOW"
        },
        "QuestionDescription": qid_description,
        "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
        "Language": []
    }
    code, body = post(
        f"survey-definitions/{SURVEY_ID}/questions",
        payload=payload,
        params={"blockId": block_id}
    )
    return code, body


def add_consent_question(block_id):
    """Add a single MC consent question with display logic that effectively
    requires acknowledgment to proceed."""
    payload = {
        "QuestionText": (
            CONSENT_TEXT
            + '<p><b>Do you consent to participate in this study?</b></p>'
        ),
        "DataExportTag": "Consent",
        "QuestionType": "MC",
        "Selector": "SAVR",
        "SubSelector": "TX",
        "Configuration": {
            "QuestionDescriptionOption": "UseText"
        },
        "QuestionDescription": "Consent to participate.",
        "Choices": {
            "1": {"Display": "Yes, I consent and wish to participate."},
            "2": {"Display": "No, I do not consent."}
        },
        "ChoiceOrder": ["1", "2"],
        "Validation": {
            "Settings": {"ForceResponse": "ON", "Type": "None"}
        },
        "Language": []
    }
    code, body = post(
        f"survey-definitions/{SURVEY_ID}/questions",
        payload=payload,
        params={"blockId": block_id}
    )
    return code, body


def add_block(block_name, description=""):
    """Create a new block. Returns block_id."""
    payload = {
        "Type": "Standard",
        "Description": block_name,
        "BlockElements": []
    }
    code, body = post(
        f"survey-definitions/{SURVEY_ID}/blocks",
        payload=payload
    )
    if code in (200, 201):
        return body["result"]["BlockID"]
    log(f"  ERROR creating block {block_name}: {code} {body}")
    return None


def update_block_randomization(block_id):
    """Set the block to randomize question order."""
    code, body = put(
        f"survey-definitions/{SURVEY_ID}/blocks/{block_id}",
        payload={
            "Type": "Standard",
            "Options": {
                "BlockLocking": "false",
                "RandomizeQuestions": "RandomWithXPrime",
                "Randomization": {
                    "Advanced": None,
                    "TotalRandSubset": ""
                },
                "BlockVisibility": "Collapsed"
            }
        }
    )
    return code, body


def add_demographics(block_id):
    """Age, gender, education, native English."""
    questions = [
        {
            "QuestionText": "What is your age?",
            "DataExportTag": "age",
            "QuestionType": "TE",
            "Selector": "SL",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "Age",
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "ValidNumber",
                                         "ValidNumber": {"Min": "18", "Max": "120"}}},
            "Language": []
        },
        {
            "QuestionText": "What is your gender?",
            "DataExportTag": "gender",
            "QuestionType": "MC",
            "Selector": "SAVR",
            "SubSelector": "TX",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "Gender",
            "Choices": {
                "1": {"Display": "Woman"},
                "2": {"Display": "Man"},
                "3": {"Display": "Non-binary / other"},
                "4": {"Display": "Prefer not to say"}
            },
            "ChoiceOrder": ["1", "2", "3", "4"],
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
            "Language": []
        },
        {
            "QuestionText": "What is the highest level of education you have completed?",
            "DataExportTag": "education",
            "QuestionType": "MC",
            "Selector": "SAVR",
            "SubSelector": "TX",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "Education",
            "Choices": {
                "1": {"Display": "Less than high school"},
                "2": {"Display": "High school / GED"},
                "3": {"Display": "Some college"},
                "4": {"Display": "Bachelor's degree"},
                "5": {"Display": "Master's degree"},
                "6": {"Display": "Doctorate or professional degree"}
            },
            "ChoiceOrder": ["1", "2", "3", "4", "5", "6"],
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
            "Language": []
        },
        {
            "QuestionText": "Are you a native English speaker?",
            "DataExportTag": "native_english",
            "QuestionType": "MC",
            "Selector": "SAVR",
            "SubSelector": "TX",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "Native English speaker",
            "Choices": {
                "1": {"Display": "Yes"},
                "2": {"Display": "No"}
            },
            "ChoiceOrder": ["1", "2"],
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
            "Language": []
        },
        {
            "QuestionText": (
                "Are there any words in this survey that you didn't recognize "
                "or didn't know the meaning of? If so, please list them here. "
                "(Optional)"
            ),
            "DataExportTag": "unknown_words",
            "QuestionType": "TE",
            "Selector": "ESTB",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "Unknown words",
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
            "Language": []
        },
        {
            "QuestionText": "Any other comments or feedback? (Optional)",
            "DataExportTag": "comments",
            "QuestionType": "TE",
            "Selector": "ESTB",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": "General feedback",
            "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
            "Language": []
        }
    ]
    for q in questions:
        code, body = post(
            f"survey-definitions/{SURVEY_ID}/questions",
            payload=q,
            params={"blockId": block_id}
        )
        if code not in (200, 201):
            log(f"  ERROR adding demographic q ({q.get('DataExportTag')}): {code} {body}")
        else:
            log(f"  OK demographic: {q.get('DataExportTag')}")


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def main():
    log(f"=== Build start: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    log(f"Survey: {SURVEY_ID}")
    log(f"Datacenter: {DATACENTER}")

    # 1. Use default block as Consent block; add consent question.
    log("\n[1] Adding consent question to default block...")
    code, body = add_consent_question(DEFAULT_BLOCK_ID)
    if code in (200, 201):
        log(f"  OK consent question (QID: {body.get('result', {}).get('QuestionID')})")
    else:
        log(f"  ERROR: {code} {body}")
        flush_log()
        return

    # 2. Add Instructions block.
    log("\n[2] Creating Instructions block...")
    instructions_block = add_block("Instructions")
    if not instructions_block:
        flush_log()
        return
    log(f"  OK block {instructions_block}")
    code, body = add_descriptive_text(instructions_block, "Instructions",
                                       INSTRUCTIONS_TEXT, "Construct tutorial.")
    if code in (200, 201):
        log(f"  OK instructions text")
    else:
        log(f"  ERROR adding instructions text: {code} {body}")

    # 3. Add Ratings block (will hold all 297 word questions).
    log("\n[3] Creating Ratings block...")
    ratings_block = add_block("Ratings")
    if not ratings_block:
        flush_log()
        return
    log(f"  OK block {ratings_block}")

    # 4. Load words and add 297 questions to the Ratings block.
    df = pd.read_csv(WORDLIST_CSV)
    words = sorted(df["Word"].astype(str).str.lower().tolist())
    log(f"\n[4] Adding {len(words)} word questions to Ratings block...")

    success_count = 0
    fail_count = 0
    for i, word in enumerate(words, 1):
        # Sanitize tag — Qualtrics export tags have to be valid identifiers
        tag = "w_" + "".join(c if c.isalnum() else "_" for c in word)[:40]
        payload = word_question_payload(word, tag)
        code, body = post(
            f"survey-definitions/{SURVEY_ID}/questions",
            payload=payload,
            params={"blockId": ratings_block}
        )
        if code in (200, 201):
            success_count += 1
            if i % 25 == 0:
                log(f"  ... {i}/{len(words)} added")
        else:
            fail_count += 1
            log(f"  FAIL [{i}] {word}: {code} {body}")
            if fail_count > 5:
                log("  >5 failures, aborting word loop early.")
                break
        time.sleep(0.05)  # gentle rate limit

    log(f"  Total: {success_count} ok, {fail_count} failed")

    # 5. Set ratings block to randomize.
    log("\n[5] Setting Ratings block to randomize question order...")
    code, body = update_block_randomization(ratings_block)
    if code in (200, 201):
        log(f"  OK randomization set")
    else:
        log(f"  WARN: could not set randomization: {code} {body}")

    # 6. Add Demographics block.
    log("\n[6] Creating Demographics block...")
    demo_block = add_block("Demographics")
    if not demo_block:
        flush_log()
        return
    log(f"  OK block {demo_block}")
    add_demographics(demo_block)

    # 7. Get full survey def to check final state.
    log("\n[7] Fetching final survey state...")
    code, body = get(f"survey-definitions/{SURVEY_ID}")
    if code in (200, 201):
        result = body.get("result", {})
        n_blocks = len(result.get("Blocks", {}))
        n_questions = len(result.get("Questions", {}))
        log(f"  OK final: {n_blocks} blocks, {n_questions} questions")
    else:
        log(f"  WARN: could not fetch final state: {code} {body}")

    # 8. Write metadata file.
    log("\n[8] Writing metadata file...")
    META_OUT.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "survey_id": SURVEY_ID,
        "datacenter": DATACENTER,
        "url_preview": f"https://{DATACENTER}.qualtrics.com/jfe/preview/{SURVEY_ID}",
        "url_edit": f"https://{DATACENTER}.qualtrics.com/Q/EditSection/Blocks?ContextSurveyID={SURVEY_ID}",
        "blocks": {
            "consent": DEFAULT_BLOCK_ID,
            "instructions": instructions_block,
            "ratings": ratings_block,
            "demographics": demo_block
        },
        "n_word_questions": success_count,
        "n_word_failures": fail_count,
        "build_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    META_OUT.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    log(f"  Wrote {META_OUT}")
    log(f"\nPreview URL: {metadata['url_preview']}")
    log(f"Edit URL:    {metadata['url_edit']}")
    log(f"\n=== Build complete: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    flush_log()


if __name__ == "__main__":
    main()
