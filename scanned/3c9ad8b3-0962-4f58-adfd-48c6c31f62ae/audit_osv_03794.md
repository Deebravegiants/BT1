# [H] ALPINE-CVE-2026-49975

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-49975
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-49975
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r1
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r3
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r3
- Alpine:v3.24: `nginx` — affected >=0 <1.30.1-r0

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache HTTP Server's mod_http leads to denial of service via malicious HTTP requests.

This issue affects Apache HTTP Server: from 2.4.17 through 2.4.67.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-49975
