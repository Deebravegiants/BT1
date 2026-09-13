# [H] ALPINE-CVE-2026-44186

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-44186
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44186
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0

## Details
Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in the mod_proxy_ftp module in Apache HTTP Server with an attacker controlled backend FTP server.

This issue affects undefined: from 2.4.0 through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44186
