# [H] ALPINE-CVE-2026-24072

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-24072
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-24072
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.67-r0

## Details
An escalation of privilege bug in various modules in Apache HTTP 2.4.66 and earlier allows local .htaccess authors to read files with the privileges of the httpd user.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-24072
