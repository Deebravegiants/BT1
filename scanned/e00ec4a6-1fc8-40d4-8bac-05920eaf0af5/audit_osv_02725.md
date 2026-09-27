# [H] ALPINE-CVE-2022-45060

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-45060
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-11-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-45060
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
An HTTP Request Forgery issue was discovered in Varnish Cache 5.x and 6.x before 6.0.11, 7.x before 7.1.2, and 7.2.x before 7.2.1. An attacker may introduce characters through HTTP/2 pseudo-headers that are invalid in the context of an HTTP/1 request line, causing the Varnish server to produce invalid HTTP/1 requests to the backend. This could, in turn, be used to exploit vulnerabilities in a server behind the Varnish server. Note: the 6.0.x LTS series (before 6.0.11) is affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-45060
