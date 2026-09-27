# [H] CVE-2017-16909

## Summary
Severity: High
Advisory: CVE-2017-16909
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2017-16909
Type: osv

## Details
An error related to the "LibRaw::panasonic_load_raw()" function (dcraw_common.cpp) in LibRaw versions prior to 0.18.6 can be exploited to cause a heap-based buffer overflow and subsequently cause a crash via a specially crafted TIFF image.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/advisories/76000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-19/
- https://usn.ubuntu.com/3615-1/
- https://github.com/LibRaw/LibRaw/commit/f1394822a0152ceed77815eafa5cac4e8baab10a
