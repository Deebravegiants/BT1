# [H] CVE-2017-17786

## Summary
Severity: High
Advisory: CVE-2017-17786
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17786
Type: osv

## Details
In GIMP 2.8.22, there is a heap-based buffer over-read in ReadImage in plug-ins/common/file-tga.c (related to bgr2rgb.part.1) via an unexpected bits-per-pixel value for an RGBA image.

## References
- http://www.openwall.com/lists/oss-security/2017/12/19/5
- http://www.securityfocus.com/bid/102765
- https://lists.debian.org/debian-lts-announce/2017/12/msg00023.html
- https://usn.ubuntu.com/3539-1/
- https://www.debian.org/security/2017/dsa-4077
- https://bugzilla.gnome.org/show_bug.cgi?id=739134
