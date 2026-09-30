# [H] MCMS Arbitrary File Deletion vulnerability

## Summary
Severity: High
Advisory: GHSA-rpvr-mw7r-25xx
CVE: CVE-2021-46062
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-rpvr-mw7r-25xx
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-basic` — affected >=0 <2.1.16
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.2.11

## Details
`net.mingsoft:ms-basic` is used for plugin management for applications built with Maven for the [Mingfei Content Management System (MCMS)](https://gitee.com/mingSoft/MCMS). ms-basic before 2.1.16 is vulnerable to arbitrary file deletion using POST requests to `/template/writeFileContent` via the `oldFileName` parameter. MCMS before 5.2.11 is also vulnerable since it bundles vulnerable versions of ms-basic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46062
- https://github.com/ming-soft/MCMS/issues/59
