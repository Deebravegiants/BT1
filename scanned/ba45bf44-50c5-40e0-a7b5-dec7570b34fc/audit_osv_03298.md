# [M] ALPINE-CVE-2025-47806

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-47806
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47806
Type: osv

## Affected
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.26.2-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.26.2-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.26.2-r0

## Details
In GStreamer through 1.26.1, the subparse plugin's parse_subrip_time function may write data past the bounds of a stack buffer, leading to a crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47806
