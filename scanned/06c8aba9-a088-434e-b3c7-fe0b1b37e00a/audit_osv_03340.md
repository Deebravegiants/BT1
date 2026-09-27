# [H] ALPINE-CVE-2025-58098

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58098
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58098
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.66-r0

## Details
Apache HTTP Server 2.4.65 and earlier with Server Side Includes (SSI) enabled and mod_cgid (but not mod_cgi) passes the shell-escaped query string to #exec cmd="..." directives.

This issue affects Apache HTTP Server before 2.4.66.

Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58098
