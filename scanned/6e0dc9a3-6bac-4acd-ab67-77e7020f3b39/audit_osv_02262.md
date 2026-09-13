# [M] ALPINE-CVE-2021-36740

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-36740
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36740
Type: osv

## Affected
- Alpine:v3.11: `varnish` — affected >=0 <6.5.2-r0
- Alpine:v3.12: `varnish` — affected >=0 <6.5.2-r0
- Alpine:v3.13: `varnish` — affected >=0 <6.5.2-r0
- Alpine:v3.14: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.15: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.16: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.17: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.18: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.19: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.20: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.21: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.22: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.23: `varnish` — affected >=0 <6.6.1-r0
- Alpine:v3.24: `varnish` — affected >=0 <6.6.1-r0

## Details
Varnish Cache, with HTTP/2 enabled, allows request smuggling and VCL authorization bypass via a large Content-Length header for a POST request. This affects Varnish Enterprise 6.0.x before 6.0.8r3, and Varnish Cache 5.x and 6.x before 6.5.2, 6.6.x before 6.6.1, and 6.0 LTS before 6.0.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36740
