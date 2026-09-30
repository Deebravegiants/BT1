# [H] ALPINE-CVE-2019-10097

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10097
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10097
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.41-r0

## Details
In Apache HTTP Server 2.4.32-2.4.39, when mod_remoteip was configured to use a trusted intermediary proxy server using the "PROXY" protocol, a specially crafted PROXY header could trigger a stack buffer overflow or NULL pointer deference. This vulnerability could only be triggered by a trusted proxy and not by untrusted HTTP clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10097
