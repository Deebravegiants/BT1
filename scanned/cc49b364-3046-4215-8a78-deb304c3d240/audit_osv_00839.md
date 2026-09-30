# [H] ALPINE-CVE-2017-9992

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9992
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9992
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=3.0 <3.1.8-r0
- Alpine:v3.5: `ffmpeg` — affected >=3.0 <3.1.8-r0
- Alpine:v3.6: `ffmpeg` — affected >=3.0 <3.2.5-r0

## Details
Heap-based buffer overflow in the decode_dds1 function in libavcodec/dfa.c in FFmpeg before 2.8.12, 3.0.x before 3.0.8, 3.1.x before 3.1.8, 3.2.x before 3.2.5, and 3.3.x before 3.3.1 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9992
