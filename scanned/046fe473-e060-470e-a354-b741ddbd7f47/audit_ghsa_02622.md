# [C] Improper Access Control in Webauthn Framework

## Summary
Severity: Critical
Advisory: GHSA-6whf-q6p5-84wg
CVE: CVE-2021-38299
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-6whf-q6p5-84wg
Type: github-advisory

## Affected
- Packagist: `web-auth/webauthn-framework` — affected >=3.3.0 <3.3.4

## Details
Webauthn Framework 3.3.x before 3.3.4 has Incorrect Access Control. An attacker that controls a user's system is able to login to a vulnerable service using an attached FIDO2 authenticator without passing a check of the user presence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38299
- https://github.com/web-auth/webauthn-framework/commit/572e239c5702667ca52487faf861abc768a46308
- https://github.com/web-auth/webauthn-framework
- https://github.com/web-auth/webauthn-framework/releases
- https://github.com/web-auth/webauthn-framework/releases/tag/v3.3.4
- https://www.fzi.de/en/news/news/detail-en/artikel/fsa-2021-1-fehlende-ueberpruefung-von-user-presence-in-webauthn-framework
