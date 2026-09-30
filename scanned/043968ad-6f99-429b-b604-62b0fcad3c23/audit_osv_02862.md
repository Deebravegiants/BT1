# [H] ALPINE-CVE-2023-38709

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-38709
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38709
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
Faulty input validation in the core of Apache allows malicious or exploitable backend/content generators to split HTTP responses.

This issue affects Apache HTTP Server: through 2.4.58.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38709
