# [M] CVE-2018-5813

## Summary
Severity: Medium
Advisory: CVE-2018-5813
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5813
Type: osv

## Details
An error within the "parse_minolta()" function (dcraw/dcraw.c) in LibRaw versions prior to 0.18.11 can be exploited to trigger an infinite loop via a specially crafted file.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-13/
- https://usn.ubuntu.com/3838-1/
- https://secuniaresearch.flexerasoftware.com/advisories/83050/
- https://github.com/LibRaw/LibRaw/commit/e47384546b43d0fd536e933249047bc397a4d88b
