import argparse
import json
import sys
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def run_search(page, base_url):
    page.goto(base_url)
    page.fill("input#search", "browser automation")
    page.click("button[type=submit]")
    # Wait for the result element to appear
    page.wait_for_selector("#search-result", state="visible", timeout=10000)
    text = page.locator("#search-result").inner_text()
    return text.strip()


def run_dynamic_dom(page, base_url):
    target_url = urljoin(base_url.rstrip("/") + "/", "dynamic")
    page.goto(target_url)
    page.click("button#load-record")
    # Wait until the exact expected text appears
    page.wait_for_function(
        """() => {
            const el = document.querySelector('#dynamic-result');
            return el && el.innerText.trim() === 'Loaded record: DYNAMIC-42';
        }""",
        timeout=15000,
    )
    text = page.locator("#dynamic-result").inner_text()
    return text.strip()


def run_pagination(page, base_url):
    target_url = urljoin(base_url.rstrip("/") + "/", "page/1")
    page.goto(target_url)
    page.click("a#next")
    # Wait for the page indicator to show the correct page
    page.wait_for_function(
        """() => {
            const h1 = document.querySelector('h1');
            return h1 && h1.innerText.trim() === 'Page 2 of 2';
        }""",
        timeout=15000,
    )
    # Now read the record text
    page.wait_for_selector("#page-record", state="visible", timeout=10000)
    text = page.locator("#page-record").inner_text()
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Playwright scenario runner")
    parser.add_argument("--base-url", required=True, help="Base URL of the application")
    parser.add_argument(
        "--scenario",
        required=True,
        choices=["search", "dynamic_dom", "pagination"],
        help="Scenario to execute",
    )
    args = parser.parse_args()

    extracted_text = None
    success = False
    final_url = ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            if args.scenario == "search":
                extracted_text = run_search(page, args.base_url)
                expected = "Found: browser automation"
                success = extracted_text == expected

            elif args.scenario == "dynamic_dom":
                extracted_text = run_dynamic_dom(page, args.base_url)
                expected = "Loaded record: DYNAMIC-42"
                success = extracted_text == expected

            elif args.scenario == "pagination":
                extracted_text = run_pagination(page, args.base_url)
                expected = "Record 2 of 2: pagination verified"
                success = extracted_text == expected

            final_url = page.url

            page.close()
            context.close()
            browser.close()
    except PlaywrightTimeoutError as e:
        # Timeout indicates the expected element/text never appeared
        extracted_text = None
        success = False
        final_url = ""
    except Exception as e:
        # Any other unexpected error
        extracted_text = None
        success = False
        final_url = ""

    result = {
        "scenario": args.scenario,
        "success": success,
        "extracted_text": extracted_text,
        "final_url": final_url,
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
