# [M] Directus inserts access token from query string into logs

## Summary
Severity: Medium
Advisory: GHSA-vw58-ph65-6rxp
CVE: CVE-2024-47822
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-vw58-ph65-6rxp
Type: github-advisory

## Affected
- npm: `@directus/api` — affected >=0 <21.0.0

## Details
### Summary
Access token from query string is not redacted and is potentially exposed in system logs which may be persisted.

### Details
The access token in `req.query` is not redacted when the `LOG_STYLE` is set to `raw`. If these logs are not properly sanitized or protected, an attacker with access to it can potentially gain administrative control, leading to unauthorized data access and manipulation.

### PoC
1. Set `LOG_LEVEL="raw"` in the environment.
2. Send a request with the `access_token` in the query string.
3. Notice that the `access_token` in `req.query` is not redacted.

### Impact
It impacts systems where the `LOG_STYLE` is set to `raw`. The `access_token` in the query could potentially be a long-lived static token. Users with impacted systems should rotate their static tokens if they were provided using query string.

## References
- https://github.com/directus/directus/security/advisories/GHSA-vw58-ph65-6rxp
- https://nvd.nist.gov/vuln/detail/CVE-2024-47822
- https://github.com/directus/directus/commit/2e893f9c576d5a02506272fe2c0bcc12e6c58768
- https://github.com/directus/directus
