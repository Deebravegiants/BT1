# [H] CVE-2017-12599

## Summary
Severity: High
Advisory: CVE-2017-12599
Aliases: GHSA-fvq6-392h-6mjj, PYSEC-2026-2820, PYSEC-2026-710
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12599
Type: osv

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 has an out-of-bounds read error in the function icvCvt_BGRA2BGR_8u_C4C3R when reading an image file by using cv::imread.

## References
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9309
