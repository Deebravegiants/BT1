# [M] ALPINE-CVE-2017-14223

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14223
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14223
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0
- Alpine:v3.7: `ffmpeg` — affected >=0 <3.3.4-r0

## Details
In libavformat/asfdec_f.c in FFmpeg 3.3.3, a DoS in asf_build_simple_index() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted ASF file, which claims a large "ict" field in the header but does not contain sufficient backing data, is provided, the for loop would consume huge CPU and memory resources, since there is no EOF check inside the loop.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14223
