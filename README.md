# 📝 Ai Text Detection Bypass Script

This script automates the process of registering on gptinf.com, a website that makes text undetectable by AI detection tools. The script uses Selenium for browser automation, including bypassing reCAPTCHA, registering with temporary email addresses, and paraphrasing large blocks of text. If the input text exceeds the website's limit, the script creates new accounts as needed and continues processing.

## Features

- Automated Account Creation: Automatically registers new accounts using temporary email addresses.
- reCAPTCHA Bypass: Bypass reCAPTCHA challenges during the registration process using audio bypass technique.
- Text Paraphrasing: Breaks down large text into chunks, paraphrases each chunk, and saves the results.
- Account Management: When paraphrasing exceeds the word limit per account, the script creates a new account and continues.
- Clipboard Integration: Retrieves paraphrased text directly from the clipboard.

## Usage

1. Clone this repository to your local machine.

```bash
git clone https://github.com/obaskly/AiDetectionBypass.git
```

2. Install the required Python packages.

  ```bash
  pip install -r requirements.txt
  ```

Prepare your article in a text file (e.g., article.txt), or paste it directly.

3. Run the script.

  ```bash
  python main.py
  ```

4. The script will create an `accounts.txt` file with temporary email accounts and save the paraphrased content to `paraphrased_text.txt`.
Sit back and relax while the script paraphrases your article!

## Prerequisites

- Python 3.x
- Google Chrome installed (chromedriver is used by Selenium)

## Script in action

https://github.com/user-attachments/assets/9eb883f3-f0a2-42b5-bd8c-a727fdde083c

