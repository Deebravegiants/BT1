# [M] ALPINE-CVE-2017-14058

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14058
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14058
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0
- Alpine:v3.7: `ffmpeg` — affected >=0 <3.3.4-r0

## Details
In FFmpeg 2.4 and 3.3.3, the read_data function in libavformat/hls.c does not restrict reload attempts for an insufficient list, which allows remote attackers to cause a denial of service (infinite loop).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14058
