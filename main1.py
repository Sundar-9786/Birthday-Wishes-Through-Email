from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
MY_EMAIL = "your mail here"
MY_PASSWORD = "password here"

# Get today's date
today = datetime.now()
today_tuple = (today.month, today.day)

# Read the birthdays CSV
data = pd.read_csv("birthdays.csv")

# Filter the rows where the birthday matches today
birthday_people = data[(data["month"] == today_tuple[0]) & (data["day"] == today_tuple[1])]

if not birthday_people.empty:
    # Read letter_2.txt
    with open("letter_templates/letter_2.txt", "r", encoding="utf-8") as letter_file:
        letter_contents = letter_file.read()
    
    # Establish email connection
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        
        # Send an email to each birthday person
        for _, person in birthday_people.iterrows():
            personalized_letter = letter_contents.replace("[NAME]", person["name"])
            
            # Create email message with UTF-8 encoding
            msg = MIMEMultipart()
            msg["From"] = MY_EMAIL
            msg["To"] = person["email"]
            msg["Subject"] = "Happy Birthday!"
            msg.attach(MIMEText(personalized_letter, "plain", "utf-8"))
            
            # Send email
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=person["email"],
                msg=msg.as_string()
            )

print("Birthday emails sent successfully!")
