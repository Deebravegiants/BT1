# [H] ALPINE-CVE-2025-13878

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-13878
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-13878
Type: osv

## Affected
- Alpine:v3.19: `bind` — affected >=0 <9.18.44-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.44-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.44-r0
- Alpine:v3.22: `bind` — affected >=0 <9.20.18-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.18-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.18-r0

## Details
Malformed BRID/HHIT records can cause `named` to terminate unexpectedly.
This issue affects BIND 9 versions 9.18.40 through 9.18.43, 9.20.13 through 9.20.17, 9.21.12 through 9.21.16, 9.18.40-S1 through 9.18.43-S1, and 9.20.13-S1 through 9.20.17-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-13878
