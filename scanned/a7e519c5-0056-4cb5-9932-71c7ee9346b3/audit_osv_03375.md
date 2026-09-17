# [M] ALPINE-CVE-2025-66200

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-66200
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-66200
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.66-r0

## Details
mod_userdir+suexec bypass via AllowOverride FileInfo vulnerability in Apache HTTP Server. Users with access to use the RequestHeader directive in htaccess can cause some CGI scripts to run under an unexpected userid.

This issue affects Apache HTTP Server: from 2.4.7 through 2.4.65.

Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-66200
