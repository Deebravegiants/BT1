# [M] SeaweedFS Vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-q97m-8853-pq76
CVE: CVE-2024-40120
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-16
Source: https://github.com/advisories/GHSA-q97m-8853-pq76
Type: github-advisory

## Affected
- Go: `github.com/seaweedfs/seaweedfs` — affected >=0 <0.0.0-20240625155419-9ac102336200

## Details
seaweedfs v3.68 was discovered to contain a SQL injection vulnerability via the component /abstract_sql/abstract_sql_store.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40120
- https://github.com/seaweedfs/seaweedfs/issues/5710
- https://github.com/seaweedfs/seaweedfs/commit/9ac1023362000f6e8e58c9d278653f5926a0d90e
- https://gist.github.com/sud0why/1b2115c1d644bd3db1c1b3f16684a78c
- https://github.com/seaweedfs/seaweedfs
- https://github.com/seaweedfs/seaweedfs/releases/tag/3.69
