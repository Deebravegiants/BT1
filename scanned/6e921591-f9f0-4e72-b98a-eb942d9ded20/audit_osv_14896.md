# [H] CVE-2019-12293

## Summary
Severity: High
Advisory: CVE-2019-12293
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2019-12293
Type: osv

## Details
In Poppler through 0.76.1, there is a heap-based buffer over-read in JPXStream::init in JPEG2000Stream.cc via data with inconsistent heights or widths.

## References
- http://www.securityfocus.com/bid/108457
- https://lists.debian.org/debian-lts-announce/2019/06/msg00002.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MAWV24KRXTFODLVT46RXI27XIQFX2QR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWS7NVFFCUY3YSTMEKZEJEU6JVUUBKHB/
- https://usn.ubuntu.com/4042-1/
- https://access.redhat.com/errata/RHSA-2019:2713
- https://gitlab.freedesktop.org/poppler/poppler/issues/768
