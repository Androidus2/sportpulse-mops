"""Check the deployed Angular/Spring Boot package without API keys or third-party calls."""

import argparse
import json
import re
import time
import urllib.error
import urllib.request


def fetch(base_url, path):
    with urllib.request.urlopen(base_url + path, timeout=10) as response:
        return response.headers.get_content_type(), response.read().decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="Application origin, e.g. http://127.0.0.1:18080")
    parser.add_argument("--wait-seconds", type=int, default=120)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    deadline = time.monotonic() + args.wait_seconds
    while True:
        try:
            content_type, body = fetch(base_url, "/api/health")
            if content_type == "application/json" and json.loads(body).get("status") == "UP":
                break
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            pass
        if time.monotonic() >= deadline:
            raise SystemExit("Application did not become healthy before the timeout")
        time.sleep(2)

    paths = ["/", "/standings", "/favorites", "/login", "/matches/42",
             "/matches/football/42", "/matches/basketball/42", "/matches/hockey/42"]
    for path in paths:
        content_type, body = fetch(base_url, path)
        if content_type != "text/html" or "<app-root>" not in body:
            raise SystemExit(f"Angular entry point missing at {path}")

    _, index = fetch(base_url, "/")
    scripts = re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', index)
    if not scripts:
        raise SystemExit("Angular JavaScript bundles missing from index.html")
    for script in scripts:
        if ":" in script or script.startswith("//"):
            raise SystemExit("Expected same-origin JavaScript bundles")
        content_type, body = fetch(base_url, "/" + script.lstrip("/"))
        if content_type not in ("text/javascript", "application/javascript") or "<app-root>" in body:
            raise SystemExit(f"JavaScript bundle was not served correctly: {script}")

    styles = re.findall(r'<link\b[^>]*\brel="stylesheet"[^>]*\bhref="([^"]+)"', index)
    if not styles:
        raise SystemExit("Angular stylesheet missing from index.html")
    for stylesheet in styles:
        if ":" in stylesheet or stylesheet.startswith("//"):
            raise SystemExit("Expected same-origin stylesheets")
        content_type, _ = fetch(base_url, "/" + stylesheet.lstrip("/"))
        if content_type != "text/css":
            raise SystemExit(f"Stylesheet was not served correctly: {stylesheet}")

    for path in ("/api/missing", "/missing-bundle.js", "/.env"):
        try:
            fetch(base_url, path)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                continue
        raise SystemExit(f"Expected a real 404 instead of Angular fallback at {path}")

    print(f"Deployment smoke test passed: health, {len(paths)} frontend routes, "
          f"{len(scripts)} JavaScript bundles, {len(styles)} stylesheets, API/asset/env 404s")


if __name__ == "__main__":
    main()
