# [M] ArcadeDB before 26.8.1 Server-Side Request Forgery via LOAD CSV

## Summary
Severity: Medium
Advisory: CVE-2026-76225
Aliases: GHSA-mmww-w3w3-6r86
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76225
Type: osv

## Details
ArcadeDB before 26.8.1 contains a server-side request forgery vulnerability in the OpenCypher LOAD CSV implementation that fails to validate HTTP/HTTPS URLs. Authenticated attackers can craft LOAD CSV queries pointing to internal network addresses or cloud metadata endpoints to make the ArcadeDB server fetch and return sensitive data from restricted services.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-mmww-w3w3-6r86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76225.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76225
- https://www.vulncheck.com/advisories/arcadedb-before-server-side-request-forgery-via-load-csv
