# [H] CVE-2019-10872

## Summary
Severity: High
Advisory: CVE-2019-10872
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-05
Source: https://osv.dev/vulnerability/CVE-2019-10872
Type: osv

## Details
An issue was discovered in Poppler 0.74.0. There is a heap-based buffer over-read in the function Splash::blitTransparent at splash/Splash.cc.

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00002.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MAWV24KRXTFODLVT46RXI27XIQFX2QR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWS7NVFFCUY3YSTMEKZEJEU6JVUUBKHB/
- https://usn.ubuntu.com/4042-1/
- http://www.securityfocus.com/bid/107862
- https://gitlab.freedesktop.org/poppler/poppler/issues/750
