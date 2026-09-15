# [H] ALPINE-CVE-2017-11399

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11399
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11399
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.7-r0

## Details
Integer overflow in the ape_decode_frame function in libavcodec/apedec.c in FFmpeg 2.4 through 3.3.2 allows remote attackers to cause a denial of service (out-of-array access and application crash) or possibly have unspecified other impact via a crafted APE file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11399
