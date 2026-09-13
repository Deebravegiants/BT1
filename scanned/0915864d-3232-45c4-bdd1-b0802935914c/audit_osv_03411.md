# [M] ALPINE-CVE-2026-10723

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-10723
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-10723
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
BIND may accept incorrect child-zone NSEC3 records as valid, which could allow an attacker to forge authenticated NXDOMAIN responses.
This issue affects BIND 9 versions 9.18.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.11.3-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-10723
