# [H] ArcadeDB before 26.8.1 Path Traversal via create/drop database

## Summary
Severity: High
Advisory: CVE-2026-75855
Aliases: GHSA-qwgr-2c45-63xx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75855
Type: osv

## Details
ArcadeDB versions before 26.8.1 fail to sanitize database names in the POST /api/v1/server endpoint's create database and drop database commands, allowing authenticated root users to write and delete arbitrary files outside the configured database directory. Attackers can supply database names containing ../ sequences to create databases at arbitrary filesystem paths or recursively delete directories the server process can access.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-qwgr-2c45-63xx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75855.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75855
- https://www.vulncheck.com/advisories/arcadedb-before-path-traversal-via-create-drop-database
