# [M] zipp Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jfmj-5v4g-7637
CVE: CVE-2024-5569
CWE: CWE-400, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-09
Source: https://github.com/advisories/GHSA-jfmj-5v4g-7637
Type: github-advisory

## Affected
- PyPI: `zipp` — affected >=0 <3.19.1

## Details
A Denial of Service (DoS) vulnerability exists in the jaraco/zipp library, affecting all versions prior to 3.19.1. The vulnerability is triggered when processing a specially crafted zip file that leads to an infinite loop. This issue also impacts the zipfile module of CPython, as features from the third-party zipp library are later merged into CPython, and the affected code is identical in both projects. The infinite loop can be initiated through the use of functions affecting the `Path` module in both zipp and zipfile, such as `joinpath`, the overloaded division operator, and `iterdir`. Although the infinite loop is not resource exhaustive, it prevents the application from responding. The vulnerability was addressed in version 3.19.1 of jaraco/zipp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5569
- https://github.com/jaraco/zipp/commit/fd604bd34f0343472521a36da1fbd22e793e14fd
- https://github.com/jaraco/zipp
- https://huntr.com/bounties/be898306-11f9-46b4-b28c-f4c4aa4ffbae
