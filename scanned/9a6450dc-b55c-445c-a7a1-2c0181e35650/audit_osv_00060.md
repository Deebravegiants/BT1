# [H] ALPINE-CVE-2016-10199

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10199
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10199
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-good` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-good1` — affected >=0 <1.10.4-r0

## Details
The qtdemux_tag_add_str_full function in gst/isomp4/qtdemux.c in gst-plugins-good in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted tag value.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10199
