# [M] ALPINE-CVE-2016-7785

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-7785
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7785
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0

## Details
The avi_read_seek function in libavformat/avidec.c in FFmpeg before 3.1.4 allows remote attackers to cause a denial of service (assert fault) via a crafted AVI file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7785
