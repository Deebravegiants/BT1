# [M] openssl-encrypt's readiness endpoint leaks database error details to unauthenticated callers

## Summary
Severity: Medium
Advisory: GHSA-2vhw-q7vh-7xv2
CWE: CWE-201
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-2vhw-q7vh-7xv2
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

The `/ready` endpoint in `openssl_encrypt_server/server.py` at **lines 159-175** catches database errors and returns the full exception string in the response.

### Affected Code

```python
except Exception as e:
    return {"status": "not_ready", "reason": str(e)}
```

### Impact

Database exception messages can leak:
- Database hostnames and IP addresses
- Connection parameters and port numbers
- Driver version information
- Potentially database credentials if included in connection string errors

This information is available to unauthenticated callers.

### Recommended Fix

- Return a generic error message: `{"status": "not_ready", "reason": "database unavailable"}`
- Log the full exception server-side for debugging

### Fix

Fixed in commit `7aa8787` on branch `releases/1.4.x` — replaced str(e) with generic "database check failed" message; full exception logged server-side at WARNING level.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-2vhw-q7vh-7xv2
- https://github.com/jahlives/openssl_encrypt/commit/7aa8787f4de2e9a23f58fca067bb16c4c69d28bb
- https://github.com/jahlives/openssl_encrypt
