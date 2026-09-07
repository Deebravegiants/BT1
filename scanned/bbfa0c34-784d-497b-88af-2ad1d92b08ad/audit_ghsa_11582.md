# [M] NocoDB has Stored Cross-site Scripting via Formula Cell

## Summary
Severity: Medium
Advisory: GHSA-vx5p-q85x-xm3c
CVE: CVE-2026-28357
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-vx5p-q85x-xm3c
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.3

## Details
### Summary
A stored XSS vulnerability exists in the Formula virtual cell. Formula results containing `URI::()` patterns are rendered via `v-html` without sanitization, allowing injected HTML to execute.

### Details
The `replaceUrlsWithLink()` function in `urlUtils.ts` converts `URI::(url)` patterns to `<a>` tags but passes all other HTML through unchanged. A user with Creator role (minimum role for formula field creation) can craft a formula like `CONCAT("URI::(https://example.com)", "<img src=x onerror=...>")` to inject arbitrary scripts rendered for all viewers.

### Impact
Credential theft via script execution in the context of users viewing the table.

### Credit
This issue was reported by [@Akokonunes](https://github.com/Akokonunes).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-vx5p-q85x-xm3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-28357
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.3
