# [M] Authentication Bypass in saml2-js

## Summary
Severity: Medium
Advisory: GHSA-mfcp-34xw-p57x
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-mfcp-34xw-p57x
Type: github-advisory

## Affected
- npm: `saml2-js` — affected >=0 <2.0.5

## Details
Versions of `saml2-js` prior to 2.0.5 are vulnerable to an Authentication Bypass. The package fails to enforce the assertion conditions for encrypted assertions, which may allow an attacker to reuse encrypted assertion tokens indefinitely.


## Recommendation

Upgrade to version 2.0.5 or later.

## References
- https://github.com/Clever/saml2/pull/190
- https://github.com/Clever/saml2/commit/ae0da4d0a0ea682a737be481e3bd78798be405c0
- https://github.com/Clever/saml2
- https://snyk.io/vuln/SNYK-JS-SAML2JS-474637
- https://www.npmjs.com/advisories/1222
