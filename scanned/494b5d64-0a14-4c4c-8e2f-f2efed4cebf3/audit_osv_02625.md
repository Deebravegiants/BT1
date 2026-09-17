# [H] ALPINE-CVE-2022-38150

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-38150
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-38150
Type: osv

## Affected
- Alpine:v3.17: `varnish` — affected >=0 <7.1.1-r0
- Alpine:v3.18: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.19: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.20: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.21: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.22: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.23: `varnish` — affected >=0 <7.0.3-r0
- Alpine:v3.24: `varnish` — affected >=0 <7.0.3-r0

## Details
In Varnish Cache 7.0.0, 7.0.1, 7.0.2, and 7.1.0, it is possible to cause the Varnish Server to assert and automatically restart through forged HTTP/1 backend responses. An attack uses a crafted reason phrase of the backend response status line. This is fixed in 7.0.3 and 7.1.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-38150
