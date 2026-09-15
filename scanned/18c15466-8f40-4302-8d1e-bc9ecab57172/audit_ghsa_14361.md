# [C] Ming-Soft MCMS vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-hx8p-9m48-g76r
CVE: CVE-2020-20913
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-hx8p-9m48-g76r
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.1

## Details
SQL Injection vulnerability found in Ming-Soft MCMS v.4.7.2 allows a remote attacker to execute arbitrary code via `basic_title` parameter. This issue is resolved in v5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20913
- https://github.com/ming-soft/MCMS/issues/27
- https://github.com/ming-soft/MCMS
