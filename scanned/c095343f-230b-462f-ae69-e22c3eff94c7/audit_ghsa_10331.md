# [M] openssl-encrypt has CORS wildcard with allow_credentials=True in standalone servers

## Summary
Severity: Medium
Advisory: GHSA-c65f-x25w-62jv
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-c65f-x25w-62jv
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

Both standalone servers configure CORS with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, and `allow_headers=["*"]`.

### Affected Code

```python
# server/key-server/app/main.py:86-92
# server/telemetry-server/app/main.py:23-29
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # defaults to ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

The docker-compose file (`openssl_encrypt_server/docker-compose.yml:75`) also defaults `CORS_ORIGINS` to `*`, and `.env.example` ships with `CORS_ORIGINS=*`.

### Impact

This is the most permissive CORS configuration possible, allowing any website to make fully credentialed cross-origin requests to the API. An attacker's website could make authenticated API calls on behalf of any user who visits it.

### Recommended Fix

- Remove wildcard defaults — require explicit origin configuration
- Never combine `allow_origins=["*"]` with `allow_credentials=True`
- Update `.env.example` with placeholder domains instead of `*`

### Fix

Fixed in commit `809416b` on branch `releases/1.4.x` — changed CORS default from ["*"] to [] in both key-server and telemetry-server; added validation rejecting wildcard when debug=False.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-c65f-x25w-62jv
- https://github.com/jahlives/openssl_encrypt/commit/809416b74d2749cdcffb484cd65b057e1685cc13
- https://github.com/jahlives/openssl_encrypt
