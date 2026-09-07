# [H] Reflected XSS from the callback handler's error query parameter

## Summary
Severity: High
Advisory: GHSA-954c-jjx6-cxv7
CVE: CVE-2021-32702
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-954c-jjx6-cxv7
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=0 <1.4.2

## Details
### Overview

Versions before and including `1.4.1` are vulnerable to reflected XSS.  An attacker can execute arbitrary code by providing an XSS payload in the `error` query parameter which is then processed by the callback handler as an error message.

### Am I affected?
You are affected by this vulnerability if you are using `@auth0/nextjs-auth0` version `1.4.1` or lower **unless** you are using custom error handling that does not return the error message in an HTML response.

### How to fix that?
Upgrade to version `1.4.2`.

### Will this update impact my users?
The fix adds basic HTML escaping to the error message and it should not impact your users.

### Credit

https://github.com/inian
https://github.com/git-ishanpatel

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-954c-jjx6-cxv7
- https://nvd.nist.gov/vuln/detail/CVE-2021-32702
- https://github.com/auth0/nextjs-auth0/commit/6996e2528ceed98627caa28abafbc09e90163ccf
- https://www.npmjs.com/package/@auth0/nextjs-auth0
