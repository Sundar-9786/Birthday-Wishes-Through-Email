# Code Quality & Security Audit Report

**Project:** Birthday Wishes Through Email  
**Repository:** Sundar-9786/Birthday-Wishes-Through-Email  
**Audit Date:** 2026-02-25  
**Files Audited:** `main1.py`, `main.ipynb`, `birthdays.csv`, `letter_2.txt`, `letter_templates/`

---

## Executive Summary

The project is a Python automation script that reads a CSV file of birthdays and sends personalized email greetings on matching dates. While the core logic is functional, the audit identified **3 critical security vulnerabilities**, **3 high-severity issues**, and **9 code quality issues** that must be addressed before this project is used in any real environment.

---

## 1. Security Issues

### 🔴 CRITICAL — Hardcoded Credentials in Source Code

**Affected files:** `main1.py` (lines 8–9), `main.ipynb`

```python
# main1.py
MY_EMAIL = "your mail here"
MY_PASSWORD = "password here"
```

Storing credentials (even placeholder values) directly in source code is dangerous. When real values are substituted, anyone with read access to the repository can extract them. This is the most common cause of account takeovers and data breaches in open-source projects.

**Recommendation:** Load credentials from environment variables or a `.env` file (excluded from version control):

```python
import os
from dotenv import load_dotenv

load_dotenv()
MY_EMAIL = os.environ["MY_EMAIL"]
MY_PASSWORD = os.environ["MY_PASSWORD"]
```

Add `python-dotenv` to dependencies and create a `.env.example` file as documentation for required variables.

---

### 🔴 CRITICAL — Real PII (Email Addresses) Committed to Version Control

**Affected file:** `birthdays.csv`

```
name,email,year,month,day
Vinoth,vinothsnega07@gmail.com ,2001,2,4
Sundar,sundarrajmech333@gmail.com,2003,2,3
Mathumitha,mathumithaananthan@gmail.com,2002,2,5
Kathir,vpkathir2@gmail.com,2004,2,3
```

Real names and personal email addresses are permanently committed to a public repository. This is a privacy violation and may violate data protection regulations (e.g., GDPR, India PDPB). Even if the repository is made private later, the data is already exposed in the Git history.

**Recommendation:**
- Replace real entries with anonymised sample data (e.g., `john.doe@example.com`).
- Add `birthdays.csv` to `.gitignore` so the production data file is never committed.
- Provide a `birthdays_sample.csv` with dummy data for reference.

---

### 🔴 CRITICAL — No `.gitignore` File

**Affected file:** *(missing)*

Without a `.gitignore`, sensitive files such as `.env`, credentials files, and personal data CSV files can be accidentally committed and pushed to the repository.

**Recommendation:** Create a `.gitignore` file that at minimum includes:

```
.env
*.csv
__pycache__/
*.pyc
.ipynb_checkpoints/
```

---

### 🟠 HIGH — SMTP Connection Without Explicit Port (Default Port 25 Risk)

**Affected file:** `main1.py` (line 27), `main.ipynb`

```python
with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
```

`smtplib.SMTP("smtp.gmail.com")` connects on port 25 by default. Most ISPs block outbound port 25 and Gmail requires STARTTLS on port 587. Relying on the default port is fragile and may fail silently or fall back to unencrypted communication.

**Recommendation:** Always specify the port explicitly:

```python
with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()
```

Alternatively, use `smtplib.SMTP_SSL("smtp.gmail.com", 465)` for implicit TLS.

---

### 🟠 HIGH — Google Account Password Authentication Deprecated

**Affected file:** `main1.py`, `main.ipynb`

Using a plain Google account password with `smtplib.login()` no longer works for most Google accounts unless "Less Secure App Access" is enabled — a setting Google has permanently removed. This approach is both broken and insecure.

**Recommendation:** Use a **Gmail App Password** (requires 2FA to be enabled on the Google account) or switch to the **Gmail API with OAuth 2.0** for production use.

---

### 🟡 MEDIUM — Trailing Whitespace in CSV Data

**Affected file:** `birthdays.csv` (line 2)

```
Vinoth,vinothsnega07@gmail.com ,2001,2,4
```

There is a trailing space after the email address `vinothsnega07@gmail.com `. This will cause `sendmail()` to attempt delivery to an invalid address (`vinothsnega07@gmail.com ` with a trailing space) and the email will silently fail or be rejected.

**Recommendation:** Strip whitespace from the email field before use:

```python
to_addr = person["email"].strip()
```

Or clean the CSV data at load time:

```python
data = pd.read_csv("birthdays.csv")
data.columns = data.columns.str.strip()
data = data.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
```

---

## 2. Code Quality Issues

### 🟠 HIGH — No Error Handling

**Affected file:** `main1.py`, `main.ipynb`

The script has no `try/except` blocks. Any runtime error — SMTP connection failure, file not found, CSV parse error, network timeout — will crash the script with an unhandled exception and no informative message.

**Recommendation:** Wrap the main logic in error handling:

```python
import logging

logging.basicConfig(level=logging.INFO)

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        for _, person in birthday_people.iterrows():
            try:
                connection.sendmail(...)
                logging.info("Email sent to %s", person["name"])
            except smtplib.SMTPException as e:
                logging.error("Failed to send email to %s: %s", person["name"], e)
except (smtplib.SMTPException, OSError) as e:
    logging.critical("SMTP connection failed: %s", e)
```

---

### 🟠 HIGH — No Input Validation

**Affected file:** `main1.py`, `main.ipynb`

The script does not validate:
- Whether `birthdays.csv` exists before reading it.
- Whether required columns (`name`, `email`, `month`, `day`) are present.
- Whether email addresses are in a valid format.
- Whether the letter template file exists.

**Recommendation:** Add validation before processing:

```python
import os, re

CSV_PATH = "birthdays.csv"
TEMPLATE_PATH = "letter_templates/letter_2.txt"

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Birthday data file not found: {CSV_PATH}")
if not os.path.exists(TEMPLATE_PATH):
    raise FileNotFoundError(f"Letter template not found: {TEMPLATE_PATH}")

required_columns = {"name", "email", "month", "day"}
if not required_columns.issubset(data.columns):
    raise ValueError(f"CSV is missing required columns: {required_columns - set(data.columns)}")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
for _, person in birthday_people.iterrows():
    if not EMAIL_REGEX.match(person["email"].strip()):
        logging.warning("Skipping invalid email for %s: '%s'", person["name"], person["email"])
```

---

### 🟡 MEDIUM — `print` Used Instead of Logging

**Affected file:** `main1.py` (line 49), `main.ipynb`

```python
print("Birthday emails sent successfully!")
```

`print` statements cannot be silenced, redirected to log files, or given severity levels. In a scheduled/automated context this makes monitoring and debugging difficult.

**Recommendation:** Replace `print` with the standard `logging` module:

```python
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.info("Birthday emails sent successfully!")
```

---

### 🟡 MEDIUM — Script Not Wrapped in `if __name__ == "__main__"`

**Affected file:** `main1.py`

Top-level code runs immediately when the file is imported. This prevents the module from being reused, tested, or imported safely.

**Recommendation:**

```python
def main():
    # ... all logic here ...

if __name__ == "__main__":
    main()
```

---

### 🟡 MEDIUM — Duplicate File: `letter_2.txt` in Repository Root

**Affected file:** `letter_2.txt` (root), `letter_templates/letter_2.txt`

The file `letter_2.txt` in the repository root is a duplicate of `letter_templates/letter_2.txt`. The script correctly reads from `letter_templates/letter_2.txt`, so the root copy serves no purpose and causes confusion.

**Recommendation:** Delete `letter_2.txt` from the repository root.

---

### 🟡 MEDIUM — Code Duplicated Between `main1.py` and `main.ipynb`

The notebook `main.ipynb` contains the exact same logic as `main1.py`. Maintaining two copies means that any bug fix or improvement must be applied twice.

**Recommendation:** Remove the notebook or refactor `main1.py` into importable functions that the notebook can call. Do not maintain two identical implementations.

---

### 🟡 MEDIUM — No `requirements.txt` or Dependency Specification

**Affected file:** *(missing)*

There is no `requirements.txt`, `setup.py`, or `pyproject.toml` listing project dependencies. Users must guess which packages to install, and there is no way to pin dependency versions for reproducibility.

**Recommendation:** Create `requirements.txt`:

```
pandas>=1.5.0
python-dotenv>=1.0.0
```

---

### 🟡 MEDIUM — Hardcoded File Paths

**Affected file:** `main1.py` (lines 16, 23)

```python
data = pd.read_csv("birthdays.csv")
with open("letter_templates/letter_2.txt", "r", encoding="utf-8") as letter_file:
```

These relative paths require the script to be run from a specific working directory. Running the script from any other directory will cause a `FileNotFoundError`.

**Recommendation:** Resolve paths relative to the script file:

```python
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "birthdays.csv")
TEMPLATE_PATH = os.path.join(BASE_DIR, "letter_templates", "letter_2.txt")
```

---

### 🟢 LOW — No Unit Tests

**Affected file:** *(missing)*

There are no tests for any part of the project. Adding even basic tests for name substitution, CSV parsing, and email validation would prevent regressions and improve confidence during future changes.

**Recommendation:** Create a `tests/` directory with at minimum:
- A test that verifies `[NAME]` replacement works correctly.
- A test that verifies CSV loading works with a sample file.
- A test that verifies invalid emails are rejected by validation logic.

---

## 3. Summary Table

| # | Severity | Category | Issue |
|---|----------|----------|-------|
| 1 | 🔴 Critical | Security | Hardcoded credentials in source code |
| 2 | 🔴 Critical | Security / Privacy | Real PII (emails) committed to version control |
| 3 | 🔴 Critical | Security | No `.gitignore` to prevent accidental secret commits |
| 4 | 🟠 High | Security | SMTP default port 25 used instead of explicit port 587 |
| 5 | 🟠 High | Security | Plain password auth (deprecated by Google) |
| 6 | 🟠 High | Code Quality | No error/exception handling |
| 7 | 🟠 High | Code Quality | No input validation |
| 8 | 🟡 Medium | Security | Trailing whitespace causes silent email delivery failure |
| 9 | 🟡 Medium | Code Quality | `print` used instead of logging |
| 10 | 🟡 Medium | Code Quality | Script not guarded with `if __name__ == "__main__"` |
| 11 | 🟡 Medium | Code Quality | Duplicate file `letter_2.txt` in root |
| 12 | 🟡 Medium | Code Quality | Logic duplicated in `main1.py` and `main.ipynb` |
| 13 | 🟡 Medium | Code Quality | No `requirements.txt` / dependency specification |
| 14 | 🟡 Medium | Code Quality | Hardcoded relative file paths |
| 15 | 🟢 Low | Code Quality | No unit tests |

---

## 4. Recommended Action Plan

**Immediate (before any real use):**
1. Remove real email addresses from `birthdays.csv` and replace with sample data.
2. Add a `.gitignore` that excludes `.env` and sensitive CSV files.
3. Move credentials to environment variables using `python-dotenv`.
4. Fix the SMTP port to `587` explicitly.

**Short-term:**
5. Add `try/except` error handling around SMTP operations and file reads.
6. Add input validation (file existence, column check, email format).
7. Replace `print` with `logging`.
8. Delete the duplicate `letter_2.txt` from the repository root.
9. Add `requirements.txt`.
10. Use script-relative paths for file access.
11. Wrap script logic in `if __name__ == "__main__"`.

**Long-term:**
12. Add unit tests in a `tests/` directory.
13. Consolidate or remove the duplicate `main.ipynb`.
14. Consider switching to Gmail API + OAuth 2.0 for production email sending.
