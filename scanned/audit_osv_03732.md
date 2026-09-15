# [M] ALPINE-CVE-2026-44119

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-44119
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44119
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0

## Details
Improper Privilege Management vulnerability in Apache HTTP Server 2.4.67 and earlier allows local .htaccess authors to read files with the privileges of the httpd user.

This issue affects Apache HTTP Server: from through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44119
