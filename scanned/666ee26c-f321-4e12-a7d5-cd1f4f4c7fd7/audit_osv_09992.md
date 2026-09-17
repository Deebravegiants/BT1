# [H] CVE-2017-12601

## Summary
Severity: High
Advisory: CVE-2017-12601
Aliases: GHSA-w96g-3p64-63wr, PYSEC-2026-2831, PYSEC-2026-716
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12601
Type: osv

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 has a buffer overflow in the cv::BmpDecoder::readData function in modules/imgcodecs/src/grfmt_bmp.cpp when reading an image file by using cv::imread, as demonstrated by the 4-buf-overflow-readData-memcpy test case.

## References
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9309
