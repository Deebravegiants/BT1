# [H] ALPINE-CVE-2020-11993

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11993
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11993
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.46-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.46-r0

## Details
Apache HTTP Server versions 2.4.20 to 2.4.43 When trace/debug was enabled for the HTTP/2 module and on certain traffic edge patterns, logging statements were made on the wrong connection, causing concurrent use of memory pools. Configuring the LogLevel of mod_http2 above "info" will mitigate this vulnerability for unpatched servers.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11993
