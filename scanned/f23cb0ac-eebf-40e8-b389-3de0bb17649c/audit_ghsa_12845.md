# [H] Arbitrary file write in net.mingsoft:ms-mcms

## Summary
Severity: High
Advisory: GHSA-65v6-3c9m-hmrp
CVE: CVE-2022-47042
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-65v6-3c9m-hmrp
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.2.11

## Details
MCMS v5.2.10 and below was discovered to contain an arbitrary file write vulnerability via the component ms/template/writeFileContent.do.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47042
- https://gitee.com/mingSoft/MCMS/issues/I6592F
- https://github.com/ming-soft/MCMS
