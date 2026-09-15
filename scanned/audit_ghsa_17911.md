# [H] simple-admin-core SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-f2m2-4q6r-cwc4
CVE: CVE-2025-51667
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-08-27
Source: https://github.com/advisories/GHSA-f2m2-4q6r-cwc4
Type: github-advisory

## Affected
- Go: `github.com/suyuan32/simple-admin-core` — affected >=1.2.0 <1.6.8

## Details
An issue was discovered in simple-admin-core v1.2.0 thru v1.6.7. The /sys-api/role/update interface in the simple-admin-core system has a limited SQL injection vulnerability, which may lead to partial data leakage or disruption of normal system operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51667
- https://github.com/suyuan32/simple-admin-core/issues/333
- https://github.com/suyuan32/simple-admin-core/commit/f1e2c4f3c55cd5953ad7f7b0706df48adaaeb18a
- https://gist.github.com/66Giraffe66/fc258f7fcc65a6a1a1a01e217977b92d
- https://github.com/suyuan32/simple-admin-core
