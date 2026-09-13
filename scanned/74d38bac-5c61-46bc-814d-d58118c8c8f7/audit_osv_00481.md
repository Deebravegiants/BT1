# [M] ALPINE-CVE-2017-14054

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14054
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14054
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0
- Alpine:v3.7: `ffmpeg` — affected >=0 <3.3.4-r0

## Details
In libavformat/rmdec.c in FFmpeg 3.3.3, a DoS in ivr_read_header() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted IVR file, which claims a large "len" field in the header but does not contain sufficient backing data, is provided, the first type==4 loop would consume huge CPU resources, since there is no EOF check inside the loop.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14054
