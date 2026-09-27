# [M] ALPINE-CVE-2016-7555

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-7555
Ecosystem: Alpine:v3.4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7555
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0

## Details
The avi_read_header function in libavformat/avidec.c in FFmpeg before 3.1.4 is vulnerable to memory leak when decoding an AVI file that has a crafted "strh" structure.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7555
