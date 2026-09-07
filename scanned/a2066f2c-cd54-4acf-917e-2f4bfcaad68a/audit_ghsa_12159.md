# [H] Parse Server exposes auth data via /users/me endpoint

## Summary
Severity: High
Advisory: GHSA-37mj-c2wf-cx96
CVE: CVE-2026-33627
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-37mj-c2wf-cx96
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.55
- npm: `parse-server` — affected >=0 <8.6.61

## Details
### Impact

An authenticated user calling `GET /users/me` receives unsanitized auth data, including sensitive credentials such as MFA TOTP secrets and recovery codes. The endpoint internally uses master-level authentication for the session query, and the master context leaks through to the user data, bypassing auth adapter sanitization. An attacker who obtains a user's session token can extract MFA secrets to generate valid TOTP codes indefinitely.

### Patches

The `/users/me` endpoint now queries the session and user data separately, using the caller's authentication context for the user query so that all security layers apply correctly.

### Workarounds

There is no known workaround.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-37mj-c2wf-cx96
- https://nvd.nist.gov/vuln/detail/CVE-2026-33627
- https://github.com/parse-community/parse-server/pull/10278
- https://github.com/parse-community/parse-server/pull/10279
- https://github.com/parse-community/parse-server/commit/5b8998e6866bcf75be7b5bb625e27d23bfaf912c
- https://github.com/parse-community/parse-server/commit/875cf10ac979bd60f70e7a0c534e2bc194d6982f
- https://github.com/parse-community/parse-server
