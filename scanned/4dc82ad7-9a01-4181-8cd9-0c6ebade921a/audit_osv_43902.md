# [C] ArcadeDB MongoDB wire protocol authentication bypass cross-database

## Summary
Severity: Critical
Advisory: CVE-2026-75852
Aliases: GHSA-fq9c-x968-g278
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75852
Type: osv

## Details
ArcadeDB versions before 26.8.1 fail to enforce SASL authentication on data commands in the MongoDB wire-protocol plugin. Unauthenticated attackers can issue insert, find, update, delete, and create commands against any database by connecting to port 27017 without credentials.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-fq9c-x968-g278
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75852.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75852
- https://www.vulncheck.com/advisories/arcadedb-mongodb-wire-protocol-authentication-bypass-cross-database
