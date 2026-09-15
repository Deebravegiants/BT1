# [H] ALPINE-CVE-2019-9928

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9928
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9928
Type: osv

## Affected
- Alpine:v3.10: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.11: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.12: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.13: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.14: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.15: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.16: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.17: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.18: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.19: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.16.0-r0
- Alpine:v3.9: `gst-plugins-base` — affected >=0 <1.14.4-r1

## Details
GStreamer before 1.16.0 has a heap-based buffer overflow in the RTSP connection parser via a crafted response from a server, potentially allowing remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9928
