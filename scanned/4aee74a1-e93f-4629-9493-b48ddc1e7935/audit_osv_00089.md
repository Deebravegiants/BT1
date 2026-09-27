# [H] ALPINE-CVE-2016-2330

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2330
Ecosystem: Alpine:v3.3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2330
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0

## Details
libavcodec/gif.c in FFmpeg before 2.8.6 does not properly calculate a buffer size, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via a crafted .tga file, related to the gif_image_write_image, gif_encode_init, and gif_encode_close functions.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2330
