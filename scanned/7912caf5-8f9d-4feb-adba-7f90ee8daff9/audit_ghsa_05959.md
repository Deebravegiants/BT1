# [M] Glances: as_dict_secure() Value-Level Bypass Leaks Credentials in URL Values via /api/4/config

## Summary
Severity: Medium
Advisory: GHSA-4h34-v6r8-mmjc
CVE: CVE-2026-68520
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-4h34-v6r8-mmjc
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.6

## Details
## Summary

Glances provides `as_dict_secure()` explicitly designed for unauthenticated API access, with a docstring stating it returns "a sanitised copy of the configuration dict" where "Sensitive keys in remaining sections are replaced by '********'". However, the implementation only checks KEY names against a regex pattern and never inspects VALUE content. The documented `[ip]` config section supports `public_api` (URL), `public_username` (login), and `public_password` (password). While `public_password` is correctly masked, both `public_api` (when containing embedded credentials like `https://user:pass@host/`) and `public_username` are returned in full to unauthenticated users via `GET /api/4/config`.

## Affected Versions

Glances latest (Docker: `nicolargo/glances:latest`)

## Root Cause

In `glances/config.py`, `as_dict_secure()`:
```python
_SECURE_SENSITIVE_KEY_RE = re.compile(r"password|token|secret|api_key|apikey|ssl_keyfile", re.IGNORECASE)

def as_dict_secure(self):
    """Return a sanitised copy of the configuration dict.
    Intended for unauthenticated API access.
    - Sensitive keys in remaining sections are replaced by '********'.
    """
    sanitized = {}
    for section, options in self.as_dict().items():
        if section in _SECURE_BLOCKED_SECTIONS: continue
        sanitized[section] = {
            key: "********" if _SECURE_SENSITIVE_KEY_RE.search(key) else value
            for key, value in options.items()
        }
    return sanitized
```

In `glances/outputs/glances_restful_api.py`:
```python
# Line 1294
args_json = self.config.as_dict() if self.args.password else self.config.as_dict_secure()
```

The `[ip]` config section documents: `public_api` (URL), `public_username` (login), `public_password` (password).
- `public_password` → matches "password" → masked ✓
- `public_api` → no match → returned in full (contains `user:pass@` in URL) ✗
- `public_username` → no match → returned in full ✗

## Impact

- Unauthenticated credential disclosure via `GET /api/4/config` or `GET /api/4/config/ip`
- `as_dict_secure()` exists specifically to protect credentials in no-auth mode but fails to mask `public_username` and credential-bearing URLs in `public_api`

## Prerequisites

- Glances in web server mode without `--password` (default, no auth)
- `glances.conf` `[ip]` section with `public_api` containing embedded credentials and/or `public_username` set

## Environment

- Glances latest (Docker: `nicolargo/glances:latest`)
- Remote Docker lab at `http://10.140.200.102:8080`

## Reproduction Steps

```bash
docker run -d --name glances-test -p 8080:61208 -e GLANCES_OPT='-w' nicolargo/glances:latest
sleep 20
docker exec glances-test sed -i 's|public_api=https://ipv4.ipleak.net/json/|public_api=https://admin:secret123@ipv4.ipleak.net/json/|' /etc/glances/glances.conf
docker exec glances-test sed -i 's|#public_username=<myname>|public_username=myname|' /etc/glances/glances.conf
docker exec glances-test sed -i 's|#public_password=<mysecret>|public_password=mysecret|' /etc/glances/glances.conf
docker restart glances-test
sleep 15
curl -s "$TARGET/api/4/config/ip"
# Returns: {"public_api": "https://admin:secret123@...", "public_username": "myname", "public_password": "********"}
```

## Evidence

See `C:/Tools/glances-config-leak-evidence.txt`.

## Dedup Check

- GHSA-gfc2-9qmw-w7vh covers CORS but NOT value-level credential leak
- No existing GHSA covers `as_dict_secure()` value-level filtering gap
- 13 published GHSA, none covering this issue

## Suggested Remediation

Add "username" and "login" to sensitive key pattern, and check values for embedded credentials in URLs.

## Disclosure Timeline

- 2026-07-28: Vulnerability discovered and verified via Docker deployment

## Reporter

GitHub username: Todor

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-4h34-v6r8-mmjc
- https://github.com/nicolargo/glances/commit/8d0f8276c2abd2e9d400bd6c84bdfba0dfcab065
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.6
