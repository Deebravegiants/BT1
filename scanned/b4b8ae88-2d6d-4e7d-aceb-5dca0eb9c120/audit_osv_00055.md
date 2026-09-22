# [C] ALPINE-CVE-2016-10191

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-10191
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10191
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0

## Details
Heap-based buffer overflow in libavformat/rtmppkt.c in FFmpeg before 2.8.10, 3.0.x before 3.0.5, 3.1.x before 3.1.6, and 3.2.x before 3.2.2 allows remote attackers to execute arbitrary code by leveraging failure to check for RTMP packet size mismatches.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10191
