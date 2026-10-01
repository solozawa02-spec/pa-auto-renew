import os
import sys
import time

import requests
from playwright.sync_api import sync_playwright

USERNAME = os.environ.get("PA_USERNAME")
PASSWORD = os.environ.get("PA_PASSWORD")
API_TOKEN = os.environ.get("PA_API_TOKEN")

if not USERNAME or not PASSWORD:
    print("Error: PA_USERNAME and PA_PASSWORD environment variables are required.")
    sys.exit(1)


def check_status_via_api():
    if not API_TOKEN:
        return None
    try:
        url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/webapps/{USERNAME}.pythonanywhere.com/"
        r = requests.get(url, headers={"Authorization": f"Token {API_TOKEN}"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[API Status] Domain: {data.get('domain_name')}, Expiry: {data.get('expiry')}, Enabled: {data.get('enabled')}")
            return data.get("expiry")
    except Exception as e:
        print(f"[API Warning] Failed to check status via API: {e}")
    return None


def main():
    print(f"=== Starting PythonAnywhere Auto-Renew for {USERNAME} ===")
    prev_expiry = check_status_via_api()

    extended = False
    reloaded = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("1. Navigating to login page...")
        page.goto("https://www.pythonanywhere.com/login/", wait_until="networkidle")

        print("2. Submitting login credentials...")
        page.fill("#id_auth-username", USERNAME)
        page.fill("#id_auth-password", PASSWORD)
        page.click("#id_next")

        page.wait_for_load_state("networkidle")
        time.sleep(3)

        if "login" in page.url:
            error = page.locator(".alert-danger, .errorlist, .help-block").all_text_contents()
            print(f"Error: Login failed! Page URL: {page.url}, Error: {error}")
            browser.close()
            sys.exit(1)

        print(f"3. Logged in successfully. Current URL: {page.url}")

        webapps_url = f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/"
        print(f"4. Navigating to Webapps tab: {webapps_url}")
        page.goto(webapps_url, wait_until="networkidle")
        time.sleep(2)

        print("5. Looking for Extend / Run until button...")
        extend_selectors = [
            "input[value*='Run until']",
            "button:has-text('Run until')",
            "input.btn-warning",
            "form[action*='extend'] input[type='submit']",
            "form[action*='extend'] button",
            "button:has-text('Extend')",
            "input[value*='Extend']"
        ]

        for sel in extend_selectors:
            btn = page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible():
                btn_text = btn.first.get_attribute("value") or btn.first.inner_text()
                print(f"Found renewal button: '{btn_text}' using selector '{sel}'. Clicking...")
                btn.first.click()
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                extended = True
                print("Renewal button clicked successfully!")
                break

        if not extended:
            print("Notice: Extend button not found or not currently active (it may already be extended recently).")

        print("6. Reloading Webapp...")
        reload_selectors = [
            "button:has-text('Reload')",
            "input[value*='Reload']",
            "#id_reload_button",
            ".reload_button",
            "button[name='reload']"
        ]
        for sel in reload_selectors:
            rbtn = page.locator(sel)
            if rbtn.count() > 0 and rbtn.first.is_visible():
                print(f"Found reload button using selector '{sel}'. Clicking...")
                rbtn.first.click()
                page.wait_for_load_state("networkidle")
                time.sleep(5)
                reloaded = True
                print("Webapp reloaded successfully via UI!")
                break

        if not reloaded and API_TOKEN:
            print("Attempting reload via API...")
            try:
                r = requests.post(
                    f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/webapps/{USERNAME}.pythonanywhere.com/reload/",
                    headers={"Authorization": f"Token {API_TOKEN}"},
                    timeout=15
                )
                if r.status_code == 200:
                    print("Reloaded successfully via API.")
                    reloaded = True
            except Exception as e:
                print(f"API reload error: {e}")

        browser.close()

    if not extended and not reloaded:
        print("Error: Neither renewal nor reload succeeded.")
        sys.exit(1)

    new_expiry = check_status_via_api()
    print(f"=== Auto-Renew Finished. Previous expiry: {prev_expiry} -> Current expiry: {new_expiry} ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
