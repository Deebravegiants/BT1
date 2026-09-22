# [M] Glances: REST API CORS Credentials Guard Uses Exact-Match Instead of Membership Test — Bypassed by Any Multi-Origin Allowlist Containing the Wildcard

## Summary
Severity: Medium
Advisory: GHSA-fp27-88fp-2phg
CVE: CVE-2026-68517
CWE: CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-fp27-88fp-2phg
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.6

## Details
### Summary
Glances's REST API server includes a documented safety check intended to guarantee that `cors_credentials=True` can never be combined with an unrestricted CORS origin allowlist. The check compares the configured origin list to the wildcard using exact list equality (`cors_origins == ["*"]`) instead of a membership test. Any multi-entry origin configuration that merely includes `"*"` alongside other origins (e.g. `cors_origins=*,https://trusted.example.com`) bypasses the check entirely, while Starlette's underlying `CORSMiddleware` still treats the presence of `"*"` anywhere in the list as "allow all origins" and reflects the request's actual `Origin` header together with `Access-Control-Allow-Credentials: true`. This allows any website to read a victim's authenticated Glances monitoring data — including full process lists with command-line arguments — by exploiting the browser's automatic replay of cached HTTP Basic Auth credentials in a cross-origin request.

### Details
`glances/outputs/glances_restful_api.py:298`:
```python
if cors_origins == ["*"] and cors_credentials:
    logger.warning(...)
    cors_credentials = False
```
The intended guarantee is documented in `glances/outputs/glances_stdout_api_restful_doc.py:247-260`: *"Setting cors_credentials=True with cors_origins=* is not allowed. Glances will automatically disable credentials and log a warning if this combination is detected."* The exact-equality comparison only matches when `cors_origins` is precisely the single-element list `["*"]`. Starlette's `CORSMiddleware`, by contrast, determines wildcard behavior via `"*" in allow_origins` — a membership test — so any multi-entry list containing `"*"` is still treated by Starlette as "allow all origins," while Glances's own guard silently fails to disable credentials for that case, breaking the documented guarantee with no warning logged.

This is the same exact-match-versus-membership-test bug shape that CVE-2026-46608 fixed in the sibling XML-RPC server (`glances/server.py`, which correctly performs `if '*' in cors_origins:`). The REST API's analogous check was never updated to the corrected pattern.

### PoC
Configuration:
```ini
[outputs]
cors_origins=*,https://trusted.example.com
cors_credentials=true
```
```
# Confirm auth is required
curl -s -i http://127.0.0.1:36212/api/4/cpu
-> 401 Unauthorized, www-authenticate: Basic

# Authenticated request, Origin header set to an arbitrary domain never configured
curl -s -i -u glances:<password> -H "Origin: https://totally-evil-attacker.com" \
  http://127.0.0.1:36212/api/4/cpu
-> 200 OK
   access-control-allow-origin: https://totally-evil-attacker.com
   access-control-allow-credentials: true
   {"total": 0.0, "user": 0.0, ...}

# Same against the process list, exposing command lines/usernames/PIDs
curl -s -u glances:<password> -H "Origin: https://totally-evil-attacker.com" \
  http://127.0.0.1:36212/api/4/processlist
-> [{"cmdline": [...], "username": "...", "pid": ..., ...}, ...]
   (same access-control-allow-origin / access-control-allow-credentials headers)
```

### Impact
Any operator who configures `cors_origins` as a multi-entry list that includes the wildcard alongside one or more specific trusted origins — a plausible configuration mistake given the documented default is the bare wildcard, and an operator attempting to additionally permit a second legitimate dashboard origin may not realize the wildcard must first be removed — silently loses the documented credentials-disable protection. Any third-party website can then read the full authenticated monitoring dataset of any visitor who has previously logged into that Glances instance via their browser, including process command-line arguments (which frequently contain secrets passed as CLI flags), usernames, and PIDs.

### Remediation suggestion
Change the check at `glances_restful_api.py:298` from `cors_origins == ["*"]` to `"*" in cors_origins`, matching the corrected pattern already used in `glances/server.py` for the XML-RPC server.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-fp27-88fp-2phg
- https://github.com/nicolargo/glances/commit/890858944ab9d03730ec6b1ba42d4015e6d85db5
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.6
