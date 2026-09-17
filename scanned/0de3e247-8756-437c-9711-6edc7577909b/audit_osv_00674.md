# [M] ALPINE-CVE-2017-5837

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5837
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5837
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-base1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-base1` — affected >=0 <1.8.3-r0

## Details
The gst_riff_create_audio_caps function in gst-libs/gst/riff/riff-media.c in gst-plugins-base in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (floating point exception and crash) via a crafted video file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5837
