# [H] CVE-2018-7588

## Summary
Severity: High
Advisory: CVE-2018-7588
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2018-7588
Type: osv

## Details
An issue was discovered in CImg v.220. A heap-based buffer over-read in load_bmp in CImg.h occurs when loading a crafted bmp image.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00033.html
- https://usn.ubuntu.com/4039-1/
- https://github.com/dtschump/CImg/issues/183
- https://github.com/xiaoqx/pocs/tree/master/cimg
