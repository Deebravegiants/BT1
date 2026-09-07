# [M] Session fixation in express-openid-connect

## Summary
Severity: Medium
Advisory: GHSA-7rg2-qxmf-hhx9
CVE: CVE-2021-41246
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-7rg2-qxmf-hhx9
Type: github-advisory

## Affected
- npm: `express-openid-connect` — affected >=2.3.0 <2.5.2

## Details
### Overview

Versions `2.3.0` up to and including `2.5.1` do not regenerate the session id and session cookie when user logs in.  This behavior opens up the application to various session fixation vulnerabilities.

### Am I affected?
You are affected by this vulnerability if you are using `express-openid-connect` version `2.3.0` up to and including `2.5.1` and use a custom session store.


### How to fix that?
Upgrade to version `>= 2.5.2`.

### Will this update impact my users?
The fix provided in patch will not affect your users.

## References
- https://github.com/auth0/express-openid-connect/security/advisories/GHSA-7rg2-qxmf-hhx9
- https://nvd.nist.gov/vuln/detail/CVE-2021-41246
- https://github.com/auth0/express-openid-connect/commit/5ab67ff2bd84f76674066b5e129b43ab5f2f430f
- https://github.com/auth0/express-openid-connect
- https://github.com/auth0/express-openid-connect/releases/tag/v2.5.2
