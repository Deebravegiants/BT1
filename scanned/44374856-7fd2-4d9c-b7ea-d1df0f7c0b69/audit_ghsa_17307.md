# [H] Weaviate OSS has path traversal vulnerability via the Shard Movement API

## Summary
Severity: High
Advisory: GHSA-hmmh-292h-3364
CVE: CVE-2025-67819
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-hmmh-292h-3364
Type: github-advisory

## Affected
- Go: `github.com/weaviate/weaviate` — affected >=1.30.0 <1.30.20
- Go: `github.com/weaviate/weaviate` — affected >=1.31.0-rc.0 <1.31.19
- Go: `github.com/weaviate/weaviate` — affected >=1.32.0-rc.0 <1.32.16
- Go: `github.com/weaviate/weaviate` — affected >=1.33.0-rc.0 <1.33.4

## Details
An issue was discovered in Weaviate OSS before 1.33.4. Due to a lack of validation of the fileName field in the transfer logic, an attacker who can call the GetFile method while a shard is in the "Pause file activity" state and the FileReplicationService is reachable can read arbitrary files accessible to the service process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67819
- https://github.com/weaviate/weaviate/commit/4ff2cc89277c264c37d0f7316d9eb6368cfc30ff
- https://github.com/weaviate/weaviate/commit/89c2270869e6d64f5b5276b8626c11cd816c6665
- https://github.com/weaviate/weaviate/commit/b18cc7ea82d80a61e7943361a6e335e3fd5a49c7
- https://github.com/advisories/GHSA-hmmh-292h-3364
- https://github.com/weaviate/weaviate
- https://weaviate.io/blog/weaviate-security-release-november-2025
