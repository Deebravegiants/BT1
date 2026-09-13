# [M] CVE-2018-5815

## Summary
Severity: Medium
Advisory: CVE-2018-5815
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5815
Type: osv

## Details
An integer overflow error within the "parse_qt()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.12 can be exploited to trigger an infinite loop via a specially crafted Apple QuickTime file.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-14/
- https://usn.ubuntu.com/3838-1/
- https://secuniaresearch.flexerasoftware.com/advisories/83507/
- https://github.com/LibRaw/LibRaw/commit/1334647862b0c90b2e8cb2f668e66627d9517b17
