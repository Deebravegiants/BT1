# [H] ALPINE-CVE-2016-9812

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9812
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9812
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-bad1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-bad1` — affected >=0 <1.8.3-r0

## Details
The gst_mpegts_section_new function in the mpegts decoder in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a too small section.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9812
