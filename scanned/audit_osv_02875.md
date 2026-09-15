# [H] ALPINE-CVE-2023-4236

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-4236
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4236
Type: osv

## Affected
- Alpine:v3.17: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.18: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.19: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.20: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.21: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.22: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.23: `bind` — affected >=9.18.0 <9.18.19-r0
- Alpine:v3.24: `bind` — affected >=9.18.0 <9.18.19-r0

## Details
A flaw in the networking code handling DNS-over-TLS queries may cause `named` to terminate unexpectedly due to an assertion failure. This happens when internal data structures are incorrectly reused under significant DNS-over-TLS query load.
This issue affects BIND 9 versions 9.18.0 through 9.18.18 and 9.18.11-S1 through 9.18.18-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4236
