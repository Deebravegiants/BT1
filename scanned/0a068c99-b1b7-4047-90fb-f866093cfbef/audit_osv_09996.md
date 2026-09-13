# [H] CVE-2017-12606

## Summary
Severity: High
Advisory: CVE-2017-12606
Aliases: GHSA-vc29-rj92-gc7j, PYSEC-2026-2830, PYSEC-2026-715
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12606
Type: osv

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 has an out-of-bounds write error in the function FillColorRow4 in utils.cpp when reading an image file by using cv::imread.

## References
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9309
