# [H] Payload has an SQL Injection via Query Handling

## Summary
Severity: High
Advisory: GHSA-7xxh-373w-35vg
CVE: CVE-2026-34747
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-7xxh-373w-35vg
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.79.1

## Details
### Impact

Certain request inputs were not properly validated. An attacker could craft requests that influence SQL query execution, potentially exposing or modifying data in collections.

### Patches

This issue has been fixed in **v3.79.1** and later. Query input validation has been hardened.

Upgrade to **v3.79.1 or later**.

### Workarounds

Until developers can upgrade:

- Limit access to endpoints that accept dynamic query inputs to trusted users only.  
- Validate or sanitize input from untrusted clients before sending it to query endpoints.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-7xxh-373w-35vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34747
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v3.79.1
