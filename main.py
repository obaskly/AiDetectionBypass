from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from RecaptchaSolver import RecaptchaSolver
from tempmail import EMail
from fake_useragent import UserAgent
import time
import re
import secrets
import string
import pyperclip
import os
import sys
import random


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
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f"user-data-dir=/tmp/{random.randint(0, 10000)}")
options.add_experimental_option("prefs", chrome_prefs)

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
        with open(file_path, 'r') as file:
            user_text = file.read()
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

def create_new_account():
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get("https://app.gptinf.com/signup/start")
    recaptchaSolver = RecaptchaSolver(driver)

    try:
        # Perform CAPTCHA solving
        t0 = time.time()
        recaptchaSolver.solveCaptcha()
        print(f"Time to solve the captcha: {time.time() - t0:.2f} seconds")
        
        # Wait and enter the email
        email = EMail()
        email_input_xpath = '//*[@id="__next"]/main/div/div/form/div[1]/input'
        print(f"Generated Email: {email.address}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, email_input_xpath))
        ).send_keys(str(email.address))  # Replace with the actual email
        
        # Wait and click the submit button
        submit_button_xpath = '/html/body/div[1]/main/div/div/form/button'
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
        )
        submit_button.click()
        print("Submit button clicked successfully.")

        # Function to check for the confirmation email and resend if necessary
        def wait_for_confirmation_email(max_attempts, initial_wait, decrement):
            attempts = 0
            while attempts < max_attempts:
                attempts += 1
                print(f"Attempt {attempts} to receive the confirmation code.")
                
                # Wait for the initial wait time before checking for the message
                time.sleep(initial_wait)
                
                # Check if the email has arrived
                try:
                    msg = email.wait_for_message()  # Wait indefinitely for the email to arrive
                    email_body = msg.body
                    
                    # Extract the confirmation code using regex
                    match = re.search(r'<strong>(\d+)</strong>', email_body)
                    if match:
                        confirmation_code = match.group(1)
                        print(f"Confirmation Code: {confirmation_code}")
                        return confirmation_code
                    else:
                        print("Confirmation code not found in the email body.")
                
                except Exception as e:
                    print(f"Error while waiting for email: {e}")
                
                # If the code is not received, click the resend button
                try:
                    resend_button_xpath = '/html/body/div[1]/main/div/div/email'
                    resend_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, resend_button_xpath))
                    )
                    resend_button.click()
                    print("Resend email button clicked.")
                    
                    # Reduce the wait time for the next attempt
                    initial_wait = max(1, initial_wait - decrement)

                except Exception as e:
                    print(f"Failed to click the resend email button: {e}")
                    break  # Stop further attempts if resend button click fails
            
            # If the code is not received after all attempts, return None
            return None

        # Attempt to get the confirmation code with retries
        confirmation_code = wait_for_confirmation_email(max_attempts=3, initial_wait=5, decrement=1)

        # If the confirmation code wasn't received after retries, restart the process
        if confirmation_code is None:
            print("Confirmation code was not received after multiple attempts. Restarting the process.")
            driver.quit()
            return create_new_account()

        # Enter the confirmation code into the input fields
        input_xpaths = [
            '/html/body/div[1]/main/div/div/div[4]/input[1]',
            '/html/body/div[1]/main/div/div/div[4]/input[2]',
            '/html/body/div[1]/main/div/div/div[4]/input[3]',
            '/html/body/div[1]/main/div/div/div[4]/input[4]',
            '/html/body/div[1]/main/div/div/div[4]/input[5]',
            '/html/body/div[1]/main/div/div/div[4]/input[6]'
        ]

        if len(confirmation_code) == len(input_xpaths):
            for i, digit in enumerate(confirmation_code):
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, input_xpaths[i]))
                ).send_keys(digit)
            print("Confirmation code entered successfully.")
        else:
            print("Confirmation code length does not match the number of input fields.")

        # Generate a password
        password_length = 12  # You can adjust the length as needed
        password_chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(password_chars) for _ in range(password_length))
        print(f"Generated Password: {password}")

        # Save the email and password to the accounts file
        with open('accounts.txt', 'a') as f:
            f.write(f"{str(email.address)}:{str(password)}\n")
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

    return driver

def process_paraphrasing(chunks):
    total_paraphrased_words = 0
    paraphrased_texts = []
    driver = create_new_account()

    for chunk in chunks:
        if total_paraphrased_words + len(chunk.split()) > 3000:
            # Re-initialize the driver and login to a new account
            driver.quit()
            driver = create_new_account()
            total_paraphrased_words = 0

        paraphrased_text = paraphrase_text(driver, chunk)
        paraphrased_texts.append(paraphrased_text)
        total_paraphrased_words += len(chunk.split())

    driver.quit()
    return paraphrased_texts

user_text = get_user_input()
chunks = list(split_text(user_text, 1000))

paraphrased_texts = process_paraphrasing(chunks)

# Save the paraphrased text to a file
output_file = "paraphrased_text.txt"
with open(output_file, 'w') as file:
    for text in paraphrased_texts:
        file.write(text + '\n')

print("Paraphrasing completed. Output saved to", output_file)
