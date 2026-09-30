# [M] CVE-2021-38114

## Summary
Severity: Medium
Advisory: CVE-2021-38114
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-38114
Type: osv

## Details
libavcodec/dnxhddec.c in FFmpeg 4.4 does not check the return value of the init_vlc function, a similar issue to CVE-2013-0868.

## References
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/PAXP193MB12624C21AE412BE95BA4D4A4B6F09%40PAXP193MB1262.EURP193.PROD.OUTLOOK.COM/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
- https://github.com/FFmpeg/FFmpeg/commit/7150f9575671f898382c370acae35f9087a30ba1
