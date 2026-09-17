# [M] CVE-2018-5800

## Summary
Severity: Medium
Advisory: CVE-2018-5800
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5800
Type: osv

## Details
An off-by-one error within the "LibRaw::kodak_ycbcr_load_raw()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.7 can be exploited to cause a heap-based buffer overflow and subsequently cause a crash.

## References
- http://www.securityfocus.com/bid/104663
- https://access.redhat.com/errata/RHSA-2018:3065
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://lists.debian.org/debian-lts-announce/2019/03/msg00036.html
- https://secuniaresearch.flexerasoftware.com/advisories/79000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-1/
- https://usn.ubuntu.com/3615-1/
- https://github.com/LibRaw/LibRaw/commit/8682ad204392b914ab1cc6ebcca9c27c19c1a4b4
