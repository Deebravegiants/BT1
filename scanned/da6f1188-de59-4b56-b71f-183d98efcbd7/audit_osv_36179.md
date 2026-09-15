# [C] Tarkov Data Manager Authentication Bypass vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-21854
Aliases: GHSA-r8w6-9xwg-6h73
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21854
Type: osv

## Details
The Tarkov Data Manager is a tool to manage the Tarkov item data. Prior to 02 January 2025, an authentication bypass vulnerability in the login endpoint allows any unauthenticated user to gain full admin access to the Tarkov Data Manager admin panel by exploiting a JavaScript prototype property access vulnerability, combined with loose equality type coercion. A series of fix commits on 02 January 2025 fixed this and other vulnerabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21854.json
- https://github.com/the-hideout/tarkov-data-manager/security/advisories/GHSA-r8w6-9xwg-6h73
- https://nvd.nist.gov/vuln/detail/CVE-2026-21854
- https://github.com/the-hideout/tarkov-data-manager/commit/f188f0abf766cefe3f1b7b4fc6fe9dad3736174a
