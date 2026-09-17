# [H] ALPINE-CVE-2026-62431

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62431
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62431
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
The logic to handle periodic Viridian STIMERs performs a division with an
unchecked user-controlled divisor value, that can be set to zero to cause a #DE
fault.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62431
