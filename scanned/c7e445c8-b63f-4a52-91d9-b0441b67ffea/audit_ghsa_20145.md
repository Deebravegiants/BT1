# [H] Cross Site Request Forgery in Mingsoft MCMS

## Summary
Severity: High
Advisory: GHSA-gp39-qj5f-43qv
CVE: CVE-2022-29647
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-gp39-qj5f-43qv
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
An issue was discovered in MCMS 5.2.7. There is a CSRF vulnerability that can add an administrator account via ms/basic/manager/save.do.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29647
- https://gist.github.com/aaaahuia/f708c6c8a320e0f3afbb9247903c4670
