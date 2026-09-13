# [H] ALPINE-CVE-2017-9996

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9996
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9996
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.8-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.8-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.5-r0

## Details
The cdxl_decode_frame function in libavcodec/cdxl.c in FFmpeg 2.8.x before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 does not exclude the CHUNKY format, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9996
