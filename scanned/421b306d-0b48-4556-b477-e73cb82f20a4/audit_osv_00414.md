# [H] ALPINE-CVE-2017-11719

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11719
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11719
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.7-r0

## Details
The dnxhd_decode_header function in libavcodec/dnxhddec.c in FFmpeg 3.0 through 3.3.2 allows remote attackers to cause a denial of service (out-of-array access) or possibly have unspecified other impact via a crafted DNxHD file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11719
