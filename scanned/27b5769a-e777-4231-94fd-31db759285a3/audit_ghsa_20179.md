# [C] Code injection in MCMS

## Summary
Severity: Critical
Advisory: GHSA-6xj9-hpq3-w3qw
CVE: CVE-2022-30506
CWE: CWE-434, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-6xj9-hpq3-w3qw
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
An arbitrary file upload vulnerability was discovered in MCMS 5.2.7, allowing an attacker to execute arbitrary code through a crafted ZIP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30506
- https://gitee.com/mingSoft/MCMS
- https://gitee.com/mingSoft/MCMS/issues/I56AID
