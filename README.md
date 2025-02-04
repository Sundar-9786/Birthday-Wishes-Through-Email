# Birthday Wishes Through Email 🎉

## 📌 Project Overview
This project automates birthday greetings via email. It reads a list of birthdays from a CSV file, selects a pre-written template, personalizes it, and sends emails using Python's **smtplib**.

## 🚀 Features
- Reads birthdays from a CSV file.
- Uses **letter templates** for personalized messages.
- Supports **multiple recipients** with the same birth date.
- Utilizes **SMTP protocol** for sending emails securely.
- Encodes emails in **UTF-8** to support emojis and special characters.

## 🛠️ Technologies Used
- **Python**
- **Pandas** (for handling CSV files)
- **smtplib** (for email sending)
- **MIME** (for structured email formatting)

## 📂 Project Structure
```
📁 Birthday-Wishes-Email
├── birthdays.csv  # CSV file with name, email, birth date
├── letter_templates
│   ├── letter_2.txt  # Template for email content
├── birthday_wisher.py  # Main Python script
├── README.md  # Project documentation
```

## 📌 How to Use
1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/birthday-wishes-email.git
   ```
2. **Install dependencies:**
   ```bash
   pip install pandas
   ```
3. **Update your email credentials** inside `birthday_wisher.py`.
4. **Run the script:**
   ```bash
   python birthday_wisher.py
   ```

## 📬 Sample Email Output
```
Subject: Happy Birthday!

🎉🎂✨ 🎈🎉 HAPPY BIRTHDAY, [NAME]! 🎉🎈 ✨🎂🎉
...
With all the love, confetti, and good vibes,
By Raju 🎈✨
```

## 📜 License
This project is open-source and free to use.

---
✉️ **Created by Raj** | 🌟 Don't forget to ⭐ the repo!

