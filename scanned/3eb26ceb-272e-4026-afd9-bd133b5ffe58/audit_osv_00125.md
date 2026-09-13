# [H] ALPINE-CVE-2016-5199

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5199
Ecosystem: Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5199
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.0.7-r0

## Details
An off by one error resulting in an allocation of zero size in FFmpeg in Google Chrome prior to 54.0.2840.98 for Mac, and 54.0.2840.99 for Windows, and 54.0.2840.100 for Linux, and 55.0.2883.84 for Android allowed a remote attacker to potentially exploit heap corruption via a crafted video file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5199
