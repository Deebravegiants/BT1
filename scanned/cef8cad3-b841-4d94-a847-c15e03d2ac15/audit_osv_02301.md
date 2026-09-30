# [H] ALPINE-CVE-2021-41524

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41524
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41524
Type: osv

## Affected
- Alpine:v3.11: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.50-r0

## Details
While fuzzing the 2.4.49 httpd, a new null pointer dereference was detected during HTTP/2 request processing, allowing an external source to DoS the server. This requires a specially crafted request. The vulnerability was recently introduced in version 2.4.49. No exploit is known to the project.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41524
