# [M] CVE-2019-10871

## Summary
Severity: Medium
Advisory: CVE-2019-10871
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-05
Source: https://osv.dev/vulnerability/CVE-2019-10871
Type: osv

## Details
An issue was discovered in Poppler 0.74.0. There is a heap-based buffer over-read in the function PSOutputDev::checkPageSlice at PSOutputDev.cc.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00024.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MAWV24KRXTFODLVT46RXI27XIQFX2QR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWS7NVFFCUY3YSTMEKZEJEU6JVUUBKHB/
- http://www.securityfocus.com/bid/107862
- https://access.redhat.com/errata/RHSA-2019:2713
- https://gitlab.freedesktop.org/poppler/poppler/issues/751
