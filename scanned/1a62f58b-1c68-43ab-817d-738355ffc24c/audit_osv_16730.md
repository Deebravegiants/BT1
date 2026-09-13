# [H] CVE-2019-9210

## Summary
Severity: High
Advisory: CVE-2019-9210
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/CVE-2019-9210
Type: osv

## Details
In AdvanceCOMP 2.1, png_compress in pngex.cc in advpng has an integer overflow upon encountering an invalid PNG size, which results in an attempted memcpy to write into a buffer that is too small. (There is also a heap-based buffer over-read.)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R56LVWC7KUNXFRKQB3Y5NX2YHFJKYZB4/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00034.html
- https://usn.ubuntu.com/3936-1/
- https://usn.ubuntu.com/3936-2/
- https://sourceforge.net/p/advancemame/bugs/277/
