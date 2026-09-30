# [H] ALPINE-CVE-2024-27316

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-27316
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27316
Type: osv

## Affected
- Alpine:v3.16: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.59-r0

## Details
HTTP/2 incoming headers exceeding the limit are temporarily buffered in nghttp2 in order to generate an informative HTTP 413 response. If a client does not stop sending headers, this leads to memory exhaustion.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27316
