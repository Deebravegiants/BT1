# [M] Open redirect in @auth0/nextjs-auth0

## Summary
Severity: Medium
Advisory: GHSA-2mqv-4j3r-vjvp
CVE: CVE-2021-43812
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-2mqv-4j3r-vjvp
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=0 <1.6.2

## Details
### Overview

Versions `<=1.6.1` do not filter out certain `returnTo` parameter values from the login url, which expose the application to an open redirect vulnerability.

### Am I affected?
You are affected by this vulnerability if you are using `@auth0/nextjs-auth0` version `<=1.6.1`.

### How to fix that?
Upgrade to version `>=1.6.2`

### Will this update impact my users?
The fix provided in the patch will not affect your users.

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-2mqv-4j3r-vjvp
- https://nvd.nist.gov/vuln/detail/CVE-2021-43812
- https://github.com/auth0/nextjs-auth0/commit/0bbd9f8a0c93af51f607f28633b5fb18c5e48ad6
- https://github.com/auth0/nextjs-auth0
