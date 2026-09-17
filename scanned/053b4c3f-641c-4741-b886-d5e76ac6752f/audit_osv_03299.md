# [M] ALPINE-CVE-2025-47807

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-47807
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47807
Type: osv

## Affected
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.26.2-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.26.2-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.26.2-r0

## Details
In GStreamer through 1.26.1, the subparse plugin's subrip_unescape_formatting function may dereference a NULL pointer while parsing a subtitle file, leading to a crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47807
