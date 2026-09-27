# [H] ALPINE-CVE-2016-7450

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7450
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7450
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0

## Details
The ff_log2_16bit_c function in libavutil/intmath.h in FFmpeg before 3.1.4 is vulnerable to reading out-of-bounds memory when it decodes a malformed AIFF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7450
