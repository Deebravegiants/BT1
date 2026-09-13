# [H] Directus: Missing Cross-Origin Opener Policy

## Summary
Severity: High
Advisory: GHSA-8m32-p958-jg99
CVE: CVE-2026-35408
CWE: CWE-346, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-8m32-p958-jg99
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
## Summary

Directus's Single Sign-On (SSO) login pages lacked a `Cross-Origin-Opener-Policy` (COOP) HTTP response header. Without this header, a malicious cross-origin window that opens the Directus login page retains the ability to access and manipulate the `window` object of that page. An attacker can exploit this to intercept and redirect the OAuth authorization flow to an attacker-controlled OAuth client, causing the victim to unknowingly grant access to their authentication provider account (e.g. Google, Discord).

## Impact

A successful attack allows the attacker to obtain an OAuth access token for the victim's third-party identity provider account. Depending on the scopes authorized, this can lead to:
- Unauthorized access to the victim's linked identity provider account
- Account takeover of the Directus instance if the attacker can authenticate using the stolen credentials or provider session

## Patches

This issue has been addressed by adding the `Cross-Origin-Opener-Policy: same-origin` HTTP response header to SSO-related endpoints. This header instructs the browser to place the page in its own browsing context group, severing any reference the opener window may hold.

## Workarounds

Users who are unable to upgrade immediately can mitigate this vulnerability by configuring their reverse proxy or web server to add the following HTTP response header to all Directus responses: `Cross-Origin-Opener-Policy: same-origin`

## References
- https://github.com/directus/directus/security/advisories/GHSA-8m32-p958-jg99
- https://nvd.nist.gov/vuln/detail/CVE-2026-35408
- https://github.com/directus/directus
