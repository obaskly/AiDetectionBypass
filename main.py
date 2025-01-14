from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from RecaptchaSolver import RecaptchaSolver
from email_utils import authenticate_gmail, generate_gmail_variation, get_gmail_service, extract_verify_link, get_message_body, wait_for_confirmation_email
from fake_useragent import UserAgent
import time
import re
import secrets
import string
import pyperclip
import os
import sys
import random


def setup_driver():
    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    chrome_prefs = {
        "profile.default_content_setting_values": {
            "clipboard": 1
        }
    }

    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument('--no-proxy-server')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-data-dir=/tmp/{random.randint(0, 10000)}")
    options.add_experimental_option("prefs", chrome_prefs)
    return webdriver.Chrome(options=options)

def get_user_input():
    choice = input("Enter '1' to input text directly or '2' to select a text file: ")

    if choice == '1':
        user_text = input("Enter the text to paraphrase: ")
        if len(user_text.split()) < 30:
            print("The text must contain at least 30 words.")
            sys.exit()
        return user_text
    elif choice == '2':
        file_path = input("Enter the path to the text file: ")
        if not os.path.exists(file_path):
            print("File not found.")
            sys.exit()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                user_text = file.read()
        except UnicodeDecodeError:
            print("Could not read the file. Please ensure the file is UTF-8 encoded.")
            sys.exit()
        if len(user_text.split()) < 30:
            print("The text must contain at least 30 words.")
            sys.exit()
        return user_text
    else:
        print("Invalid choice.")
        sys.exit()

def split_text(text, chunk_size):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

def paraphrase_text(driver, text_chunk):
    textarea_xpath = '/html/body/div[1]/main/section/div[1]/div[1]/div[1]/textarea'
    paraphrase_button_xpath = '/html/body/div[1]/main/section/div[2]/div[2]/button'
    clear_button_xpath = '/html/body/div[1]/main/section/div[1]/div[1]/div[1]/img'
    copy_img_xpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[4]/img'
    copy_img_css_selector = "img[title='Copy to clipboard']"
    skip_button_xpath = '/html/body/div[1]/main/div[1]/div/div/div[3]/button[1]'
    
    try:
        # Check and click the skip button if it appears
        try:
            skip_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, skip_button_xpath))
            )
            skip_button.click()
            print("Skipped the questionnaire.")
        except TimeoutException:
            print("No questionnaire to skip.")

        # Enter the text into the textarea
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, textarea_xpath))
        ).send_keys(text_chunk)
        
        # Scroll the paraphrase button into view
        paraphrase_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, paraphrase_button_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", paraphrase_button)
        
        # Ensure the paraphrase button is clickable
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, paraphrase_button_xpath))
        )
        driver.execute_script("arguments[0].click();", paraphrase_button)
        
        # Click the clear button
        clear_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, clear_button_xpath))
        )
        driver.execute_script("arguments[0].click();", clear_button)
        
        # Enter the text into the textarea again
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, textarea_xpath))
        ).send_keys(text_chunk)
        
        # Ensure the paraphrase button is clickable again
        paraphrase_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, paraphrase_button_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", paraphrase_button)
        driver.execute_script("arguments[0].click();", paraphrase_button)

        # Wait for the copy button to appear and click it
        try:
            copy_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, copy_img_xpath))
            )
        except TimeoutException:
            # If XPath fails, try using CSS selector
            copy_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, copy_img_css_selector))
            )

        # Click the copy button using JavaScript to avoid potential issues with visibility
        driver.execute_script("arguments[0].click();", copy_button)

        # Get the paraphrased text from the clipboard
        paraphrased_text = pyperclip.paste()
        return paraphrased_text

    except WebDriverException as e:
        print(f"WebDriverException: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_new_account(driver, base_email):
    driver.get("https://app.gptinf.com/signup/start")
    recaptchaSolver = RecaptchaSolver(driver)

    try:
        # Perform CAPTCHA solving
        t0 = time.time()
        recaptchaSolver.solveCaptcha()
        print(f"Time to solve the captcha: {time.time() - t0:.2f} seconds")
        
        # Wait and enter the email
        email_variant = generate_gmail_variation(base_email)
        email_input_xpath = '//*[@id="__next"]/main/div/div/form/div[1]/input'
        print(f"Generated Email: {email_variant}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, email_input_xpath))
        ).send_keys(str(email_variant))
        
        # Wait and click the submit button
        submit_button_xpath = '/html/body/div[1]/main/div/div/form/button'
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
        )
        submit_button.click()
        print("Submit button clicked successfully.")

        try:
            creds = authenticate_gmail()
            service = get_gmail_service(creds)
            confirmation_email = wait_for_confirmation_email(service)
            
            if confirmation_email:
                message_body = get_message_body(confirmation_email)
                verify_link = extract_verify_link(message_body)
            
                if verify_link:
                    try:
                        driver.get(verify_link)
                        print("Navigated to the verification link successfully.")
                    except Exception as e:
                        print(f"Error navigating to the verification link: {e}")
                else:
                    print("No verification link found.")
                
        except Exception as e:
            print(f"Error while waiting for email: {e}")

        # Generate a password
        password_length = 12  # You can adjust the length as needed
        password_chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(password_chars) for _ in range(password_length))
        print(f"Generated Password: {password}")

        # Save the email and password to the accounts file
        with open('accounts.txt', 'a') as f:
            f.write(f"{str(email_variant)}:{str(password)}\n")
        print("Account saved to file successfully.")

        # Enter the password and confirm it
        password_input_xpath = '/html/body/div[1]/main/div[1]/form/div[1]/input'
        confirm_password_input_xpath = '/html/body/div[1]/main/div[1]/form/div[2]/input'
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, password_input_xpath))
        ).send_keys(password)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, confirm_password_input_xpath))
        ).send_keys(password)
        
        print("Password and confirmation entered successfully.")

        # Click on the checkbox
        checkbox_xpath = '/html/body/div[1]/main/div[1]/form/div[3]/label/span/div'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, checkbox_xpath))
        ).click()
        print("Checkbox clicked successfully.")

        # Click on the final submit button
        final_submit_button_xpath = '/html/body/div[1]/main/div[1]/form/button'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, final_submit_button_xpath))
        ).click()
        print("Final submit button clicked successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()

def process_paraphrasing(chunks, base_email):
    total_paraphrased_words = 0
    paraphrased_texts = []
    driver = None

    try:
        for chunk in chunks:
            if driver is None or total_paraphrased_words + len(chunk.split()) > 3000:
                # Ensure the previous driver is closed
                if driver:
                    driver.quit()
                
                # Create a new account and driver
                confirmation_code = None
                driver = setup_driver()
                create_new_account(driver, base_email)

                total_paraphrased_words = 0

            # Use the driver to paraphrase the chunk
            paraphrased_text = paraphrase_text(driver, chunk)
            paraphrased_texts.append(paraphrased_text)
            total_paraphrased_words += len(chunk.split())

    except Exception as e:
        print(f"An error occurred during paraphrasing: {e}")
    
    finally:
        if driver:
            driver.quit()

    return paraphrased_texts

def main():
    try:
        # Get user input
        user_text = get_user_input()

        # Split text into chunks
        chunks = list(split_text(user_text, 1000))

        # Get the base email
        base_email = input("Enter your Gmail address: ")

        # Process paraphrasing
        paraphrased_texts = process_paraphrasing(chunks, base_email)

        # Save the paraphrased text to a file
        output_file = "paraphrased_text.txt"
        with open(output_file, 'w') as file:
            for text in paraphrased_texts:
                file.write(text + '\n')

        print("Paraphrasing completed. Output saved to", output_file)
    
    except Exception as e:
        print(f"An error occurred in the script: {e}")

if __name__ == "__main__":
    main()
