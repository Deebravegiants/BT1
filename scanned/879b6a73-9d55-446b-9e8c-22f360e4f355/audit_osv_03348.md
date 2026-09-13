# [H] ALPINE-CVE-2025-58150

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58150
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58150
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r4
- Alpine:v3.21: `xen` — affected >=0 <4.19.4-r1
- Alpine:v3.22: `xen` — affected >=0 <4.20.2-r1
- Alpine:v3.23: `xen` — affected >=0 <4.20.2-r1
- Alpine:v3.24: `xen` — affected >=0 <4.21.0-r2

## Details
Shadow mode tracing code uses a set of per-CPU variables to avoid
cumbersome parameter passing.  Some of these variables are written to
with guest controlled data, of guest controllable size.  That size can
be larger than the variable, and bounding of the writes was missing.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58150
