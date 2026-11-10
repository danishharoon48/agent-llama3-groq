import argparse
import json
import sys
from playwright.sync_api import sync_playwright


def run_search(base_url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(base_url)
            page.fill("input#search", "browser automation")
            page.click("button[type=submit]")
            page.wait_for_selector("#search-result")
            text = page.locator("#search-result").inner_text().strip()
            success = text == "Found: browser automation"
            return {
                "scenario": "search",
                "success": success,
                "extracted_text": text if success else None,
                "final_url": page.url,
            }
        finally:
            browser.close()


def run_dynamic_dom(base_url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(f"{base_url}/dynamic")
            page.click("button#load-record")
            page.wait_for_selector("#dynamic-result", state="visible")
            # Wait until the text contains the expected content
            page.wait_for_function(
                "document.querySelector('#dynamic-result') && "
                "document.querySelector('#dynamic-result').textContent.trim() === 'Loaded record: DYNAMIC-42'"
            )
            text = page.locator("#dynamic-result").inner_text().strip()
            success = text == "Loaded record: DYNAMIC-42"
            return {
                "scenario": "dynamic_dom",
                "success": success,
                "extracted_text": text if success else None,
                "final_url": page.url,
            }
        finally:
            browser.close()


def run_pagination(base_url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(f"{base_url}/page/1")
            page.click("a#next")
            # Wait for h1 to indicate Page 2 of 2
            page.wait_for_function(
                "document.querySelector('h1') && "
                "document.querySelector('h1').textContent.trim() === 'Page 2 of 2'"
            )
            page.wait_for_selector("#page-record", state="visible")
            text = page.locator("#page-record").inner_text().strip()
            success = text == "Record 2 of 2: pagination verified"
            return {
                "scenario": "pagination",
                "success": success,
                "extracted_text": text if success else None,
                "final_url": page.url,
            }
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Browser automation scenarios")
    parser.add_argument("--base-url", required=True, help="Base URL of the benchmark server")
    parser.add_argument("--scenario", required=True, choices=["search", "dynamic_dom", "pagination"],
                        help="Scenario to run")
    args = parser.parse_args()

    if args.scenario == "search":
        result = run_search(args.base_url)
    elif args.scenario == "dynamic_dom":
        result = run_dynamic_dom(args.base_url)
    elif args.scenario == "pagination":
        result = run_pagination(args.base_url)
    else:
        result = {
            "scenario": args.scenario,
            "success": False,
            "extracted_text": None,
            "final_url": None,
        }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
