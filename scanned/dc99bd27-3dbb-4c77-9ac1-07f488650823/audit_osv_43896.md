# [M] ArcadeDB before 26.8.1 Arbitrary File Read via LOAD CSV

## Summary
Severity: Medium
Advisory: CVE-2026-75842
Aliases: GHSA-hfp5-6gcp-8c75
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75842
Type: osv

## Details
ArcadeDB versions before 26.8.1 contain an arbitrary file read vulnerability in the OpenCypher LOAD CSV FROM clause that allows authenticated users to read local files. Attackers with read query privileges can use the file:// protocol in LOAD CSV statements to access arbitrary files with server process privileges, exfiltrating sensitive data directly in query responses.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-hfp5-6gcp-8c75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75842.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75842
- https://www.vulncheck.com/advisories/arcadedb-before-arbitrary-file-read-via-load-csv
