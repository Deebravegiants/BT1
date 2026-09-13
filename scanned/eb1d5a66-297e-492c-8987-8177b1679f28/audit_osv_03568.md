# [H] ALPINE-CVE-2026-3104

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3104
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3104
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=9.20.0 <9.20.21-r0
- Alpine:v3.23: `bind` — affected >=9.20.0 <9.20.21-r0
- Alpine:v3.24: `bind` — affected >=9.20.0 <9.20.21-r0

## Details
A specially crafted domain can be used to cause a memory leak in a BIND resolver simply by querying this domain.
This issue affects BIND 9 versions 9.20.0 through 9.20.20, 9.21.0 through 9.21.19, and 9.20.9-S1 through 9.20.20-S1.
BIND 9 versions 9.18.0 through 9.18.46 and 9.18.11-S1 through 9.18.46-S1 are NOT affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3104
