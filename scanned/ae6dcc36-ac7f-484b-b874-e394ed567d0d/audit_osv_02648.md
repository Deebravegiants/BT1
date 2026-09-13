# [H] ALPINE-CVE-2022-41556

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41556
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41556
Type: osv

## Affected
- Alpine:v3.15: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.16: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.17: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.18: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.19: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.20: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.21: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.22: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.23: `lighttpd` — affected >=1.4.56 <1.4.67-r0
- Alpine:v3.24: `lighttpd` — affected >=1.4.56 <1.4.67-r0

## Details
A resource leak in gw_backend.c in lighttpd 1.4.56 through 1.4.66 could lead to a denial of service (connection-slot exhaustion) after a large amount of anomalous TCP behavior by clients. It is related to RDHUP mishandling in certain HTTP/1.1 chunked situations. Use of mod_fastcgi is, for example, affected. This is fixed in 1.4.67.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41556
