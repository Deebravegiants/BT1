# [M] ALPINE-CVE-2017-5025

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5025
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5025
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.7-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.4-r0

## Details
FFmpeg in Google Chrome prior to 56.0.2924.76 for Linux, Windows and Mac, failed to perform proper bounds checking, which allowed a remote attacker to potentially exploit heap corruption via a crafted video file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5025
