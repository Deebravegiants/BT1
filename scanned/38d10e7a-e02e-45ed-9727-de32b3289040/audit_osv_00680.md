# [H] ALPINE-CVE-2017-5845

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5845
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5845
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-good` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-good1` — affected >=0 <1.10.4-r0

## Details
The gst_avi_demux_parse_ncdt function in gst/avi/gstavidemux.c in gst-plugins-good in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (invalid memory read and crash) via a ncdt sub-tag that "goes behind" the surrounding tag.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5845
