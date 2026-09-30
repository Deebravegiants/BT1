# [H] ALPINE-CVE-2017-14767

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14767
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14767
Type: osv

## Affected
- Alpine:v3.4: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.5: `ffmpeg` — affected >=0 <3.1.11-r0
- Alpine:v3.6: `ffmpeg` — affected >=0 <3.2.8-r0

## Details
The sdp_parse_fmtp_config_h264 function in libavformat/rtpdec_h264.c in FFmpeg before 3.3.4 mishandles empty sprop-parameter-sets values, which allows remote attackers to cause a denial of service (heap buffer overflow) or possibly have unspecified other impact via a crafted sdp file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14767
