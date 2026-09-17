# [H] Hutool allows remote code execution (RCE) via the QLExpressEngine class

## Summary
Severity: High
Advisory: GHSA-gcfh-36x4-mgj6
CVE: CVE-2025-56769
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-gcfh-36x4-mgj6
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-extra` — affected >=0 <5.8.40

## Details
An issue was discovered in chinabugotech hutool before 5.8.40 allowing attackers to execute arbitrary expressions that lead to arbitrary method invocation and potentially remote code execution (RCE) via the QLExpressEngine class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56769
- https://github.com/chinabugotech/hutool/issues/3994
- https://github.com/chinabugotech/hutool/commit/3d0d8dea4bc2fac2e9b45dc67244195f30e42e4b
- https://github.com/chinabugotech/hutool
