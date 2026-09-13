# [H] ALPINE-CVE-2022-45059

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-45059
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-11-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-45059
Type: osv

## Affected
- Alpine:v3.17: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.18: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.19: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.20: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.21: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.22: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.23: `varnish` — affected >=0 <7.2.1-r0
- Alpine:v3.24: `varnish` — affected >=0 <7.2.1-r0

## Details
An issue was discovered in Varnish Cache 7.x before 7.1.2 and 7.2.x before 7.2.1. A request smuggling attack can be performed on Varnish Cache servers by requesting that certain headers are made hop-by-hop, preventing the Varnish Cache servers from forwarding critical headers to the backend.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-45059
