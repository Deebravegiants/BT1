# [H] Strapi core vulnerable to sensitive data exposure via CORS misconfiguration

## Summary
Severity: High
Advisory: GHSA-9329-mxxw-qwf8
CVE: CVE-2025-53092
CWE: CWE-200, CWE-284, CWE-364, CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-9329-mxxw-qwf8
Type: github-advisory

## Affected
- npm: `@strapi/core` — affected >=0 <5.20.0

## Details
### Summary

A CORS misconfiguration vulnerability exists in default installations of Strapi where attacker-controlled origins are improperly reflected in API responses.

### Technical Details

By default, Strapi reflects the value of the Origin header back in the Access-Control-Allow-Origin response header without proper validation or whitelisting.

Example:
`Origin: http://localhost:8888`
`Access-Control-Allow-Origin: http://localhost:8888`
`Access-Control-Allow-Credentials: true`

This allows an attacker-controlled site (on a different port, like 8888) to send credentialed requests to the Strapi backend on 1337.

### Suggested Fix

1. Explicitly whitelist trusted origins
2. Avoid reflecting dynamic origins

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-9329-mxxw-qwf8
- https://nvd.nist.gov/vuln/detail/CVE-2025-53092
- https://github.com/strapi/strapi/commit/6e535cb756
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v5.20.0
