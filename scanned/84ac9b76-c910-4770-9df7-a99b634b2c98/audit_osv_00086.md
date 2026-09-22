# [M] ALPINE-CVE-2016-2213

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2213
Ecosystem: Alpine:v3.3
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2213
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0

## Details
The jpeg2000_decode_tile function in libavcodec/jpeg2000dec.c in FFmpeg before 2.8.6 allows remote attackers to cause a denial of service (out-of-bounds array read access) via crafted JPEG 2000 data.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2213
