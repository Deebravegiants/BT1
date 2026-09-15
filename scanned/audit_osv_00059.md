# [M] ALPINE-CVE-2016-10198

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10198
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10198
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-good` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-good1` — affected >=0 <1.10.4-r0

## Details
The gst_aac_parse_sink_setcaps function in gst/audioparsers/gstaacparse.c in gst-plugins-good in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (invalid memory read and crash) via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10198
