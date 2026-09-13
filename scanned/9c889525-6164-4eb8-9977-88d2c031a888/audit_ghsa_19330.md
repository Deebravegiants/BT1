# [C] BRCC Incorrect Access Control vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w7xj-pj5f-8pwh
CVE: CVE-2025-45616
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-w7xj-pj5f-8pwh
Type: github-advisory

## Affected
- Maven: `com.baidu.mapp:brcc-core` — affected >=0

## Details
Incorrect access control in the /admin/** API of brcc v1.2.0 allows attackers to gain access to Admin rights via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-45616
- https://github.com/baidu/brcc/issues/194
- https://github.com/baidu/brcc
