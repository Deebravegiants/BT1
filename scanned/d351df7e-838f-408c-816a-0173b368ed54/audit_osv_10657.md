# [M] CVE-2017-18013

## Summary
Severity: Medium
Advisory: CVE-2017-18013
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-01
Source: https://osv.dev/vulnerability/CVE-2017-18013
Type: osv

## Details
In LibTIFF 4.0.9, there is a Null-Pointer Dereference in the tif_print.c TIFFPrintDirectory function, as demonstrated by a tiffinfo crash.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00033.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00034.html
- https://usn.ubuntu.com/3602-1/
- https://usn.ubuntu.com/3606-1/
- http://www.securityfocus.com/bid/102345
- https://www.debian.org/security/2018/dsa-4100
- http://bugzilla.maptools.org/show_bug.cgi?id=2770
- https://gitlab.com/libtiff/libtiff/commit/c6f41df7b581402dfba3c19a1e3df4454c551a01
