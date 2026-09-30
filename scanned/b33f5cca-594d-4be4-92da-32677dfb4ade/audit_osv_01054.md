# [M] ALPINE-CVE-2018-17189

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-17189
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-17189
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.38-r0

## Details
In Apache HTTP server versions 2.4.37 and prior, by sending request bodies in a slow loris way to plain resources, the h2 stream for that request unnecessarily occupied a server thread cleaning up that incoming data. This affects only HTTP/2 (mod_http2) connections.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-17189
