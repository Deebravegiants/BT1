# [H] ALPINE-CVE-2017-9993

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9993
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9993
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=3.0 <3.1.9-r0
- Alpine:v3.5: `ffmpeg` — affected >=3.0 <3.1.9-r0
- Alpine:v3.6: `ffmpeg` — affected >=3.0 <3.2.6-r0

## Details
FFmpeg before 2.8.12, 3.0.x and 3.1.x before 3.1.9, 3.2.x before 3.2.6, and 3.3.x before 3.3.2 does not properly restrict HTTP Live Streaming filename extensions and demuxer names, which allows attackers to read arbitrary files via crafted playlist data.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9993
