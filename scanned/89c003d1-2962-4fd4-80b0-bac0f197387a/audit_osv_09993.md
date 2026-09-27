# [H] CVE-2017-12603

## Summary
Severity: High
Advisory: CVE-2017-12603
Aliases: GHSA-6v6p-p97v-g2p7, PYSEC-2026-2809, PYSEC-2026-701
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12603
Type: osv

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 has an invalid write in the cv::RLByteStream::getBytes function in modules/imgcodecs/src/bitstrm.cpp when reading an image file by using cv::imread, as demonstrated by the 2-opencv-heapoverflow-fseek test case.

## References
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9309
