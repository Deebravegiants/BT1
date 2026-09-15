# [H] CVE-2018-5817

## Summary
Severity: High
Advisory: CVE-2018-5817
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-20
Source: https://osv.dev/vulnerability/CVE-2018-5817
Type: osv

## Details
A type confusion error within the "unpacked_load_raw()" function within LibRaw versions prior to 0.19.1 (internal/dcraw_common.cpp) can be exploited to trigger an infinite loop.

## References
- https://usn.ubuntu.com/3989-1/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00036.html
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-27/
- https://www.libraw.org/news/libraw-0-19-2-release
