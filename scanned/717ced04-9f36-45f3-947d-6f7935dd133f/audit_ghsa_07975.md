# [M] Qwik City has a CSRF Protection Bypass via Content-Type Header Validation

## Summary
Severity: Medium
Advisory: GHSA-r666-8gjf-4v5f
CVE: CVE-2026-25151
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-r666-8gjf-4v5f
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.19.0

## Details
### Summary
Qwik City’s server-side request handler inconsistently interprets HTTP request headers, which can be abused by a remote attacker to circumvent form submission CSRF protections using specially crafted or multi-valued Content-Type headers.

### Impact
A vulnerability in checkCSRF lets an attacker bypass Origin-based CSRF checks by using malformed or multi-valued Content-Type headers. Exploitation requires the CORS preflight to succeed (so it’s blocked if preflight is denied) and is possible when the application accepts cross-origin requests or via non-browser clients. Impact varies with server CORS and cookie policies and may enable unauthorized state changes.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-r666-8gjf-4v5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25151
- https://github.com/QwikDev/qwik/commit/eebf610e04cc3a690f11e10191d09ff0fca1c7ed
- https://github.com/QwikDev/qwik
