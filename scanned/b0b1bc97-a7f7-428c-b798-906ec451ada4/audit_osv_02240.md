# [H] ALPINE-CVE-2021-3497

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3497
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3497
Type: osv

## Affected
- Alpine:v3.13: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.14: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.15: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.16: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.17: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.18: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.19: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.20: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.21: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.22: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.23: `gstreamer` — affected >=0.10.0 <1.18.4-r0
- Alpine:v3.24: `gstreamer` — affected >=0.10.0 <1.18.4-r0

## Details
GStreamer before 1.18.4 might access already-freed memory in error code paths when demuxing certain malformed Matroska files.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3497
