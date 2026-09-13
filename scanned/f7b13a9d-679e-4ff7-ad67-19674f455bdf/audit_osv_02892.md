# [H] ALPINE-CVE-2023-44487

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-44487
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-44487
Type: osv

## Affected
- Alpine:v3.15: `lighttpd` — affected >=0 <1.4.73-r0
- Alpine:v3.16: `lighttpd` — affected >=0 <1.4.73-r0
- Alpine:v3.17: `lighttpd` — affected >=0 <1.4.73-r0
- Alpine:v3.15: `nghttp2` — affected >=0 <1.46.0-r2
- Alpine:v3.16: `nghttp2` — affected >=0 <1.47.0-r2
- Alpine:v3.17: `nghttp2` — affected >=0 <1.51.0-r2
- Alpine:v3.18: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.19: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.20: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.21: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.22: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.23: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.24: `nghttp2` — affected >=0 <1.57.0-r0
- Alpine:v3.15: `nginx` — affected >=1.9.5 <1.20.2-r2
- Alpine:v3.16: `nginx` — affected >=1.9.5 <1.22.1-r1
- Alpine:v3.17: `nginx` — affected >=1.9.5 <1.22.1-r1
- Alpine:v3.18: `nginx` — affected >=1.9.5 <1.24.0-r7
- Alpine:v3.19: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.20: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.21: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.22: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.23: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.24: `nginx` — affected >=1.9.5 <1.24.0-r12
- Alpine:v3.17: `varnish` — affected >=0 <7.3.2-r0
- Alpine:v3.18: `varnish` — affected >=0 <7.3.1-r0

## Details
The HTTP/2 protocol allows a denial of service (server resource consumption) because request cancellation can reset many streams quickly, as exploited in the wild in August through October 2023.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-44487
