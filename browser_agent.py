import sys
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def extract_info(url: str) -> dict:
    result = {"url": url, "title": None, "heading": None}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(url, wait_until="load", timeout=30000)
            except PlaywrightTimeoutError:
                # Navigation timed out; continue with whatever is loaded
                pass

            # Title
            try:
                result["title"] = page.title()
            except Exception:
                result["title"] = None

            # Main heading (prefer first <h1>)
            try:
                h1 = page.query_selector("h1")
                if h1:
                    result["heading"] = h1.inner_text().strip() or None
                else:
                    result["heading"] = None
            except Exception:
                result["heading"] = None

            context.close()
            browser.close()
    except Exception:
        # In case Playwright itself fails, keep result with None values
        pass
    return result

def main():
    default_url = "https://example.com"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    info = extract_info(url)
    print(json.dumps(info, ensure_ascii=False))

if __name__ == "__main__":
    main()
