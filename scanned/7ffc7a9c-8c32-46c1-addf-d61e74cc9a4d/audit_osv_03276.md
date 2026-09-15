# [H] ALPINE-CVE-2025-40778

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-40778
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-40778
Type: osv

## Affected
- Alpine:v3.19: `bind` — affected >=0 <9.18.41-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.41-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.41-r0
- Alpine:v3.22: `bind` — affected >=0 <9.20.15-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.15-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.15-r0

## Details
Under certain circumstances, BIND is too lenient when accepting records from answers, allowing an attacker to inject forged data into the cache.
This issue affects BIND 9 versions 9.11.0 through 9.16.50, 9.18.0 through 9.18.39, 9.20.0 through 9.20.13, 9.21.0 through 9.21.12, 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.39-S1, and 9.20.9-S1 through 9.20.13-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-40778
