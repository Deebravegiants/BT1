# [M] Directus tokens are not redacted in flow logs, exposing session credentials to all admin

## Summary
Severity: Medium
Advisory: GHSA-f24x-rm6g-3w5v
CVE: CVE-2025-53886
CWE: CWE-200, CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-f24x-rm6g-3w5v
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.9.0

## Details
### Summary

When using Directus Flows with the WebHook trigger, all incoming request details are logged including security sensitive data like access and refresh tokens in cookies.

### Impact

Malicious admins with access to the logs can hijack the user sessions within the token expiration time of them triggering the Flow.

## References
- https://github.com/directus/directus/security/advisories/GHSA-f24x-rm6g-3w5v
- https://nvd.nist.gov/vuln/detail/CVE-2025-53886
- https://github.com/directus/directus/commit/859f664f56fb50401c407b095889cea38ff580e5
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.9.0
