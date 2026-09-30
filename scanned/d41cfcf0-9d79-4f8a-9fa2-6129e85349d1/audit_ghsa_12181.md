# [H] auth0-js Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-3rpr-mg43-xhq4
CVE: CVE-2017-17068
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2017-12-21
Source: https://github.com/advisories/GHSA-3rpr-mg43-xhq4
Type: github-advisory

## Affected
- npm: `auth0-js` — affected >=0 <8.12.0

## Details
A cross-origin vulnerability has been discovered in the Auth0 auth0.js library affecting versions &lt; 8.12. This vulnerability allows an attacker to acquire authenticated users' tokens and invoke services on a user's behalf if the target site or application uses a popup callback page with `auth0.popup.callback()`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17068
- https://appcheck-ng.com/appcheck-discovers-vulnerability-auth0-library-cve-2017-17068
- https://auth0.com/docs/security/bulletins/cve-2017-17068
- https://github.com/advisories/GHSA-3rpr-mg43-xhq4
