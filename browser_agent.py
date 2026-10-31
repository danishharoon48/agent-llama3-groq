import argparse
import json
import sys
from playwright.sync_api import sync_playwright


def run_search(base_url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.fill("input#search", "browser automation")
            page.click("button[type=submit]")
            page.wait_for_selector("#search-result", state="visible")
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
            page.goto(f"{base_url}/dynamic", wait_until="domcontentloaded")
            page.click("button#load-record")
            page.wait_for_function(
                """() => {
                    const el = document.querySelector('#dynamic-result');
                    return el && el.textContent.trim() === 'Loaded record: DYNAMIC-42';
                }""",
                timeout=10000,
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
            page.goto(f"{base_url}/page/1", wait_until="domcontentloaded")
            page.click("a#next")
            page.wait_for_function(
                """() => {
                    const h1 = document.querySelector('h1');
                    return h1 && h1.textContent.trim() === 'Page 2 of 2';
                }""",
                timeout=10000,
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
    parser.add_argument(
        "--scenario",
        required=True,
        choices=["search", "dynamic_dom", "pagination"],
        help="Scenario to run",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    scenario = args.scenario

    if scenario == "search":
        result = run_search(base_url)
    elif scenario == "dynamic_dom":
        result = run_dynamic_dom(base_url)
    elif scenario == "pagination":
        result = run_pagination(base_url)
    else:
        result = {
            "scenario": scenario,
            "success": False,
            "extracted_text": None,
            "final_url": None,
        }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
