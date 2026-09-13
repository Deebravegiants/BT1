# [M] `libavcodec/dnxhddec.c` in FFmpeg 4.4 does not check the return value of the `init_vlc` function, a...

## Summary
Severity: Medium
Advisory: JLSEC-2025-115
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-115
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <4.4.2+0

## Details
`libavcodec/dnxhddec.c` in FFmpeg 4.4 does not check the return value of the `init_vlc` function, a similar issue to CVE-2013-0868.

## References
- https://github.com/FFmpeg/FFmpeg/commit/7150f9575671f898382c370acae35f9087a30ba1
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/PAXP193MB12624C21AE412BE95BA4D4A4B6F09%40PAXP193MB1262.EURP193.PROD.OUTLOOK.COM/
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
