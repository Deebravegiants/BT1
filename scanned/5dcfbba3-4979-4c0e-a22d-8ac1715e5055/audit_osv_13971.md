# [H] CVE-2018-5808

## Summary
Severity: High
Advisory: CVE-2018-5808
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5808
Type: osv

## Details
An error within the "find_green()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.9 can be exploited to cause a stack-based buffer overflow and subsequently execute arbitrary code.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://lists.debian.org/debian-lts-announce/2019/03/msg00036.html
- https://secuniaresearch.flexerasoftware.com/advisories/81800/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-9/
- https://github.com/LibRaw/LibRaw/commit/fd6330292501983ac75fe4162275794b18445bd9
