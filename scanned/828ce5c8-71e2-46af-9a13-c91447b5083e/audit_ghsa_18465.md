# [M] Directus is vulnerable to sensitive data exposure as user data is not being redacted when logged

## Summary
Severity: Medium
Advisory: GHSA-x3vm-88hf-gpxp
CVE: CVE-2025-53885
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-x3vm-88hf-gpxp
Type: github-advisory

## Affected
- npm: `directus` — affected >=9.0.0 <11.9.0

## Details
### Summary

When using Directus Flows to handle CRUD events for users it is possible to log the incoming data to console using the "Log to Console" operation and a template string. 

### Impact

Malicious admins can log sensitive data from other users when they are created or updated.

### Workarounds
Avoid logging sensitive data to the console outside the context of development.

## References
- https://github.com/directus/directus/security/advisories/GHSA-x3vm-88hf-gpxp
- https://nvd.nist.gov/vuln/detail/CVE-2025-53885
- https://github.com/directus/directus/pull/25355
- https://github.com/directus/directus/commit/859f664f56fb50401c407b095889cea38ff580e5
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.9.0
