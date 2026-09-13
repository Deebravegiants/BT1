# [H] ALPINE-CVE-2023-5679

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-5679
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5679
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=9.16.12 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=9.16.12 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=9.16.12 <9.18.24-r0

## Details
A bad interaction between DNS64 and serve-stale may cause `named` to crash with an assertion failure during recursive resolution, when both of these features are enabled.
This issue affects BIND 9 versions 9.16.12 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.16.12-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5679
