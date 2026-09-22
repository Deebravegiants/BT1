# [H] Weaviate OSS has a Path Traversal Vulnerability via Backup ZipSlip

## Summary
Severity: High
Advisory: GHSA-7v39-2hx7-7c43
CVE: CVE-2025-67818
CWE: CWE-22, CWE-61
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-7v39-2hx7-7c43
Type: github-advisory

## Affected
- Go: `github.com/weaviate/weaviate` — affected >=0 <1.30.20
- Go: `github.com/weaviate/weaviate` — affected >=1.31.0-rc.0 <1.31.19
- Go: `github.com/weaviate/weaviate` — affected >=1.32.0-rc.0 <1.32.16
- Go: `github.com/weaviate/weaviate` — affected >=1.33.0-rc.0 <1.33.4

## Details
An issue was discovered in Weaviate OSS before 1.33.4. An attacker with access to insert data into the database can craft an entry name with an absolute path (e.g., /etc/...) or use parent directory traversal (../../..) to escape the restore root when a backup is restored, potentially creating or overwriting files in arbitrary locations within the application's privilege scope.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67818
- https://github.com/weaviate/weaviate/commit/169df2dc92bc232df62e8fab0a20db2e5371f7aa
- https://github.com/weaviate/weaviate/commit/89c2270869e6d64f5b5276b8626c11cd816c6665
- https://github.com/advisories/GHSA-7v39-2hx7-7c43
- https://github.com/weaviate/weaviate
- https://weaviate.io/blog/weaviate-security-release-november-2025
