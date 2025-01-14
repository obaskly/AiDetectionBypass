# 📝 Ai Text Detection Bypass Script

This script automates the process of registering on [gptinf.com](https://www.gptinf.com/), a website that makes text undetectable by AI detection tools. The script uses Selenium for browser automation, including bypassing reCAPTCHA, registering with generated gmail email addresses, and paraphrasing large blocks of text. If the input text exceeds the website's limit, the script creates new accounts as needed and continues processing.

## ✨ What's New?
You can Try the Other tool as well https://github.com/obaskly/AiTextDetectionBypass

## 🛑 Disclaimer

This script automates text paraphrasing but is **NOT responsible for the quality or accuracy of the output**. Please review and verify results independently.

## Features

- Gmail-Based Registration: Automates Gmail registration and verification for seamless paraphrasing. (NEW!)
- reCAPTCHA Bypass: Bypass reCAPTCHA challenges during the registration process using audio bypass technique.
- Text Paraphrasing: Breaks down large text into chunks, paraphrases each chunk, and saves the results.
- Account Management: When paraphrasing exceeds the word limit per account, the script creates a new account and continues.
- Clipboard Integration: Retrieves paraphrased text directly from the clipboard.

## Usage

1. **Clone this repository to your local machine**

```bash
git clone https://github.com/obaskly/AiDetectionBypass.git
cd AiDetectionBypass
```

2. **Install the required Python packages**

  ```bash
  pip install -r requirements.txt
  ```

3. **Install FFmpeg**

- Linux:

  ```
  sudo apt-get update
  sudo apt-get install ffmpeg
  ```
  
- Windows:

  Follow this tutorial: https://www.wikihow.com/Install-FFmpeg-on-Windows

4. **GMAIL Setup**.

- go to https://console.cloud.google.com
- create new project
- click on 'api and services'
- type "Gmail API" and select it from the results.
- Click the Enable button.
  
  #### Set Up OAuth Consent Screen
  
- In the left-hand menu, go to APIs & Services > OAuth consent screen.
- Choose External 
- Add the necessary scopes: https://www.googleapis.com/auth/gmail.readonly
- Go to the Test users section.
- Add the Gmail address you want to use for paraphrasing.
- Click Save and Continue.
  
  #### Create OAuth 2.0 Credentials
  
- Go to APIs & Services > Credentials.
- Click Create Credentials > OAuth 2.0 Client IDs.
- Choose Desktop App as the application type.
- Download the **credentials.json** file once it’s created and put it in the **json_files** folder.

5. **Run the script**

Prepare your article in a text file (e.g., article.txt), or paste it directly.

  ```bash
  python main.py
  ```

5. The script will create an `accounts.txt` file with generated emails and save the paraphrased content to `paraphrased_text.txt`.
Sit back and relax while the script paraphrases your article!

**Note: First time using the script will require getting the token file. When the webpage is open, click on the same email that you have entered in the terminal. Close the script and run it again.
This is a one time process so you won't have to do it again.**

## Prerequisites

- Python 3.x
- Google Chrome installed (chromedriver is used by Selenium)

## TODO List

- [ ] Make a GUI.
- [ ] Choose between the default word-based splitting method or a more advanced NLTK-powered sentence-preserving approach.

## Script in action

https://github.com/user-attachments/assets/9eb883f3-f0a2-42b5-bd8c-a727fdde083c

