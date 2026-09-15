# [M] Turbo: Login callback CSRF/session fixation

## Summary
Severity: Medium
Advisory: GHSA-hcf7-66rw-9f5r
CVE: CVE-2026-45773
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:L/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-hcf7-66rw-9f5r
Type: github-advisory

## Affected
- npm: `turbo` — affected >=0 <2.9.14

## Details
### Impact

Turborepo's self-hosted login and SSO browser flows did not validate a CSRF state value on the localhost callback. While the CLI was waiting for authentication, a malicious web page could send a request to the local callback server with an attacker-controlled token. If accepted before the legitimate callback, the CLI could complete login with the wrong credentials.

This affects users authenticating the `turbo` CLI against self-hosted remote cache/auth endpoints. Vercel-hosted login flows using device authorization are not affected.

### Fix

The login and SSO redirect flows now generate a random state value, include it in the browser authentication URL, and require the same value on the localhost callback before accepting a token. Callbacks with a missing or mismatched state are rejected.

### Workarounds

If you cannot upgrade immediately, avoid browser-based self-hosted `turbo login` or SSO flows on machines that may load untrusted web content during authentication. Use a pre-provisioned token or environment-based authentication instead.

## References
- https://github.com/vercel/turborepo/security/advisories/GHSA-hcf7-66rw-9f5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45773
- https://github.com/vercel/turborepo
