# [M] OpenClaw: Zalo webhook rate limiting could be bypassed before secret validation

## Summary
Severity: Medium
Advisory: GHSA-5m9r-p9g7-679c
CVE: CVE-2026-34505
CWE: CWE-307
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-5m9r-p9g7-679c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

The Zalo webhook handler applied request rate limiting only after webhook authentication succeeded. Requests with an invalid secret returned `401` but did not count against the rate limiter, allowing repeated secret guesses without triggering `429`.

### Impact

This made brute-force guessing materially easier for weak but policy-compliant webhook secrets. Once the secret was guessed, an attacker could submit forged Zalo webhook traffic.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Rate limiting now applies before successful authentication is required, closing the pre-auth brute-force gap. Users should update to `2026.3.12` or later and prefer strong webhook secrets.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5m9r-p9g7-679c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34505
- https://github.com/openclaw/openclaw/pull/44173
- https://github.com/openclaw/openclaw/commit/f96ba87f033a14183fa0ede912df3a592eef55ff
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
- https://www.vulncheck.com/advisories/openclaw-webhook-rate-limiting-bypass-via-pre-authentication-secret-validation
