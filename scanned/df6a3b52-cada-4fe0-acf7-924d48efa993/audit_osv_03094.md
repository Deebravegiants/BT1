# [H] ALPINE-CVE-2024-42516

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-42516
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-42516
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.64-r0

## Details
HTTP response splitting in the core of Apache HTTP Server allows an attacker who can manipulate the Content-Type response headers of applications hosted or proxied by the server can split the HTTP response.

This vulnerability was described as CVE-2023-38709 but the patch included in Apache HTTP Server 2.4.59 did not address the issue.

Users are recommended to upgrade to version 2.4.64, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-42516
