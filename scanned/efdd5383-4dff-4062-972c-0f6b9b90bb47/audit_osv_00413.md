# [H] ALPINE-CVE-2017-11665

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11665
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11665
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.10-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.7-r0

## Details
The ff_amf_get_field_value function in libavformat/rtmppkt.c in FFmpeg 3.3.2 allows remote RTMP servers to cause a denial of service (Segmentation Violation and application crash) via a crafted stream.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11665
