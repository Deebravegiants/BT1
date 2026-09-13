# [M] CVE-2017-17760

## Summary
Severity: Medium
Advisory: CVE-2017-17760
Aliases: GHSA-jcxv-2j3h-mg59, PYSEC-2026-2823, PYSEC-2026-711
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-29
Source: https://osv.dev/vulnerability/CVE-2017-17760
Type: osv

## Details
OpenCV 3.3.1 has a Buffer Overflow in the cv::PxMDecoder::readData function in grfmt_pxm.cpp, because an incorrect size value is used.

## References
- http://www.securityfocus.com/bid/102974
- https://lists.debian.org/debian-lts-announce/2018/01/msg00008.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://github.com/opencv/opencv/issues/10351
- https://github.com/opencv/opencv/pull/10369/commits/7bbe1a53cfc097b82b1589f7915a2120de39274c
