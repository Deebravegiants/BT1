# [H] CVE-2018-5802

## Summary
Severity: High
Advisory: CVE-2018-5802
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5802
Type: osv

## Details
An error within the "kodak_radc_load_raw()" function (internal/dcraw_common.cpp) related to the "buf" variable in LibRaw versions prior to 0.18.7 can be exploited to cause an out-of-bounds read memory access and subsequently cause a crash.

## References
- https://access.redhat.com/errata/RHSA-2018:3065
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://lists.debian.org/debian-lts-announce/2019/03/msg00036.html
- https://secuniaresearch.flexerasoftware.com/advisories/79000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-1/
- https://usn.ubuntu.com/3615-1/
- https://github.com/LibRaw/LibRaw/commit/8682ad204392b914ab1cc6ebcca9c27c19c1a4b4
