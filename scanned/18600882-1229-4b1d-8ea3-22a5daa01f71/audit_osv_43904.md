# [C] ArcadeDB Redis Wire-Protocol Plugin Missing Authentication

## Summary
Severity: Critical
Advisory: CVE-2026-75854
Aliases: GHSA-m46c-jh3x-xwrp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75854
Type: osv

## Details
ArcadeDB versions before 26.8.1 contain a missing authentication vulnerability in the Redis wire-protocol plugin that allows unauthenticated attackers to read, write, and delete data. Attackers can connect to the Redis port and execute arbitrary commands against any database on the server without providing credentials, bypassing all security gates.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-m46c-jh3x-xwrp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75854.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75854
- https://www.vulncheck.com/advisories/arcadedb-redis-wire-protocol-plugin-missing-authentication
