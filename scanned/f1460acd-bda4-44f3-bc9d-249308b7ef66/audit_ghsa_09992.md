# [M] openssl-encrypt accepts refresh tokens as URL query parameters causing token leakage

## Summary
Severity: Medium
Advisory: GHSA-4rh7-jwg9-m28m
CWE: CWE-598
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-4rh7-jwg9-m28m
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

Refresh tokens are accepted as URL query parameters in the keyserver and telemetry server routes.

### Affected Code

```python
# openssl_encrypt_server/modules/keyserver/routes.py:214-215
# openssl_encrypt_server/modules/telemetry/routes.py:90-91
async def refresh_token(
    request: Request,
    refresh_token: str = Query(..., description="Refresh token")
):
```

### Impact

Tokens in URL query parameters are exposed in:
- Server access logs
- Proxy/CDN logs
- Browser history
- HTTP Referer headers
- Network monitoring tools

This creates significant token leakage risk.

### Recommended Fix

- Accept refresh tokens in the request body (POST) instead of query parameters
- Use `Body(...)` instead of `Query(...)`

### Fix

Fixed in commit `4b2adb0` on branch `releases/1.4.x` — moved refresh token from Query parameter to POST body via RefreshRequest Pydantic model.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-4rh7-jwg9-m28m
- https://github.com/jahlives/openssl_encrypt/commit/4b2adb05cde8a7ee03cdd271755da3b377c68011
- https://github.com/jahlives/openssl_encrypt
