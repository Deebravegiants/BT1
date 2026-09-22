# [M] ALPINE-CVE-2016-9811

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9811
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9811
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-base1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-base1` — affected >=0 <1.8.3-r0

## Details
The windows_icon_typefind function in gst-plugins-base in GStreamer before 1.10.2, when G_SLICE is set to always-malloc, allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted ico file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9811
