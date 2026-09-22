# [M] CVE-2018-5801

## Summary
Severity: Medium
Advisory: CVE-2018-5801
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5801
Type: osv

## Details
An error within the "LibRaw::unpack()" function (src/libraw_cxx.cpp) in LibRaw versions prior to 0.18.7 can be exploited to trigger a NULL pointer dereference.

## References
- https://access.redhat.com/errata/RHSA-2018:3065
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://lists.debian.org/debian-lts-announce/2019/03/msg00036.html
- https://secuniaresearch.flexerasoftware.com/advisories/79000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-1/
- https://usn.ubuntu.com/3615-1/
- https://github.com/LibRaw/LibRaw/commit/0df5490b985c419de008d32168650bff17128914
