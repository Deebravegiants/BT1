# [M] CVE-2018-5268

## Summary
Severity: Medium
Advisory: CVE-2018-5268
Aliases: GHSA-9g8h-pjm4-q92p, PYSEC-2026-2814, PYSEC-2026-705
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-08
Source: https://osv.dev/vulnerability/CVE-2018-5268
Type: osv

## Details
In OpenCV 3.3.1, a heap-based buffer overflow happens in cv::Jpeg2KDecoder::readComponent8u in modules/imgcodecs/src/grfmt_jpeg2000.cpp when parsing a crafted image file.

## References
- http://www.securityfocus.com/bid/106945
- https://lists.debian.org/debian-lts-announce/2018/04/msg00019.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://github.com/opencv/opencv/issues/10541
