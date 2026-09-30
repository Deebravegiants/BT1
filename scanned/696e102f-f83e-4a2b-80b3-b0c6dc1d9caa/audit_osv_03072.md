# [H] ALPINE-CVE-2024-38473

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-38473
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-38473
Type: osv

## Affected
- Alpine:v3.17: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.60-r0

## Details
Encoding problem in mod_proxy in Apache HTTP Server 2.4.59 and earlier allows request URLs with incorrect encoding to be sent to backend services, potentially bypassing authentication via crafted requests.
Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-38473
