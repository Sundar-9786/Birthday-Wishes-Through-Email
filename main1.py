"""
Birthday Wishes Through Email
------------------------------
Reads birthdays from birthdays.csv and sends personalised birthday emails
via Gmail SMTP to anyone whose birthday matches today's date.

Required environment variables:
    BIRTHDAY_EMAIL    – Gmail address used to send emails
    BIRTHDAY_PASSWORD – Gmail App Password for that account
"""

import logging
import os
import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

BASE_DIR = Path(__file__).parent


def load_credentials() -> tuple[str, str]:
    """Load email credentials from environment variables."""
    email = os.environ.get("BIRTHDAY_EMAIL")
    password = os.environ.get("BIRTHDAY_PASSWORD")
    if not email or not password:
        raise EnvironmentError(
            "BIRTHDAY_EMAIL and BIRTHDAY_PASSWORD environment variables must be set."
        )
    return email, password


def send_birthday_emails() -> None:
    """Check today's birthdays and send personalised emails."""
    my_email, my_password = load_credentials()

    today = datetime.now()
    today_tuple = (today.month, today.day)

    # Read the birthdays CSV
    data = pd.read_csv(BASE_DIR / "birthdays.csv")
    # Strip accidental whitespace from email column
    data["email"] = data["email"].str.strip()

    birthday_people = data[
        (data["month"] == today_tuple[0]) & (data["day"] == today_tuple[1])
    ]

    if birthday_people.empty:
        logging.info("No birthdays today.")
        return

    # Read a random letter template
    import random
    templates = list((BASE_DIR / "letter_templates").glob("*.txt"))
    template_path = random.choice(templates)

    try:
        with open(template_path, "r", encoding="utf-8") as letter_file:
            letter_contents = letter_file.read()
    except OSError as exc:
        logging.error("Could not read template file %s: %s", template_path, exc)
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(my_email, my_password)

            for _, person in birthday_people.iterrows():
                recipient = person["email"]
                if not _EMAIL_RE.match(recipient):
                    logging.warning("Skipping invalid email address: %r", recipient)
                    continue

                personalized_letter = letter_contents.replace("[NAME]", person["name"])

                msg = MIMEMultipart()
                msg["From"] = my_email
                msg["To"] = recipient
                msg["Subject"] = "Happy Birthday!"
                msg.attach(MIMEText(personalized_letter, "plain", "utf-8"))

                try:
                    connection.sendmail(
                        from_addr=my_email,
                        to_addrs=recipient,
                        msg=msg.as_string(),
                    )
                    logging.info("Birthday email sent to %s", recipient)
                except smtplib.SMTPException as exc:
                    logging.error("Failed to send email to %s: %s", recipient, exc)

    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed. Check BIRTHDAY_EMAIL and BIRTHDAY_PASSWORD.")
    except smtplib.SMTPException as exc:
        logging.error("SMTP error: %s", exc)


if __name__ == "__main__":
    send_birthday_emails()
