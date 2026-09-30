# [M] CVE-2017-14136

## Summary
Severity: Medium
Advisory: CVE-2017-14136
Aliases: GHSA-634c-v2xv-ffpg, PYSEC-2026-2808, PYSEC-2026-700
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14136
Type: osv

## Details
OpenCV (Open Source Computer Vision Library) 3.3 has an out-of-bounds write error in the function FillColorRow1 in utils.cpp when reading an image file by using cv::imread. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-12597.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9443
- https://github.com/opencv/opencv/pull/9448
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
