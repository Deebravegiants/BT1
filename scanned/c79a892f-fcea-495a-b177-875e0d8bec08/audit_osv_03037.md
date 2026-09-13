# [H] ALPINE-CVE-2024-30156

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-30156
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-30156
Type: osv

## Affected
- Alpine:v3.17: `varnish` — affected >=0 <7.3.2-r0
- Alpine:v3.18: `varnish` — affected >=0 <7.3.2-r0
- Alpine:v3.19: `varnish` — affected >=0 <7.4.3-r0
- Alpine:v3.20: `varnish` — affected >=0 <7.5.0-r0
- Alpine:v3.21: `varnish` — affected >=0 <7.5.0-r0
- Alpine:v3.22: `varnish` — affected >=0 <7.5.0-r0
- Alpine:v3.23: `varnish` — affected >=0 <7.5.0-r0
- Alpine:v3.24: `varnish` — affected >=0 <7.5.0-r0

## Details
Varnish Cache before 7.3.2 and 7.4.x before 7.4.3 (and before 6.0.13 LTS), and Varnish Enterprise 6 before 6.0.12r6, allows credits exhaustion for an HTTP/2 connection control flow window, aka a Broke Window Attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-30156
