# [H] ALPINE-CVE-2017-14169

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14169
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14169
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0
- Alpine:v3.7: `ffmpeg` — affected >=0 <3.3.4-r0

## Details
In the mxf_read_primer_pack function in libavformat/mxfdec.c in FFmpeg 3.3.3 -> 2.4, an integer signedness error might occur when a crafted file, which claims a large "item_num" field such as 0xffffffff, is provided. As a result, the variable "item_num" turns negative, bypassing the check for a large value.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14169
