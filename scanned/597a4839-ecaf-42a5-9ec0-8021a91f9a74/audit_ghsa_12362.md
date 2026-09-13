# [H] Mingsoft MCMS SQL injection

## Summary
Severity: High
Advisory: GHSA-3vvh-8c65-32j4
CVE: CVE-2023-50578
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-3vvh-8c65-32j4
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
Mingsoft MCMS v5.2.9 was discovered to contain a SQL injection vulnerability via the categoryType parameter at /content/list.do.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50578
- https://gitee.com/mingSoft/MCMS/issues/I8MAJK
- https://github.com/ming-soft/MCMS
