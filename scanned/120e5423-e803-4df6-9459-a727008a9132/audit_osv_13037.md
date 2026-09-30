# [M] CVE-2018-17000

## Summary
Severity: Medium
Advisory: CVE-2018-17000
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-17000
Type: osv

## Details
A NULL pointer dereference in the function _TIFFmemcmp at tif_unix.c (called from TIFFWriteDirectoryTagTransferfunction) in LibTIFF 4.0.9 allows an attacker to cause a denial-of-service through a crafted tiff file. This vulnerability can be triggered by the executable tiffcp.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00041.html
- http://www.securityfocus.com/bid/105342
- https://lists.debian.org/debian-lts-announce/2019/02/msg00026.html
- https://usn.ubuntu.com/3906-1/
- https://www.debian.org/security/2020/dsa-4670
- http://bugzilla.maptools.org/show_bug.cgi?id=2811
