# [C] ALPINE-CVE-2026-44631

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-44631
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44631
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0

## Details
Buffer Underwrite vulnerability in Apache HTTP Server on crafted regular expressions in the configuration.

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44631
