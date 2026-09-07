# [H] Auth0-js bypasses CSRF checks

## Summary
Severity: High
Advisory: GHSA-wpq7-q8j4-72jg
CVE: CVE-2018-7307
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-07
Source: https://github.com/advisories/GHSA-wpq7-q8j4-72jg
Type: github-advisory

## Affected
- npm: `auth0-js` — affected >=0 <9.3.0

## Details
The Auth0.js library has a vulnerability affecting versions below 9.3 that allows an attacker to bypass the CSRF check from the state parameter if it's missing from the authorization response, leaving the client vulnerable to CSRF attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7307
- https://auth0.com/docs/security/bulletins/cve-2018-7307
- https://github.com/advisories/GHSA-wpq7-q8j4-72jg
