# [H] ALPINE-CVE-2026-48913

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48913
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48913
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0

## Details
Use After Free vulnerability in Apache HTTP Server module mod_http2 when file handles are already exhausted.

This issue affects Apache HTTP Server: from 2.4.55 through 2.4.67.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48913
