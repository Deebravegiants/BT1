# [C] ALPINE-CVE-2026-14739

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-14739
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14739
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI versions before 1.650 for Perl have a heap overflow when preparsing SQL statements with an extreme number of placeholders.

The fix for CVE-2026-10879 did not allocate enough memory to handle approximately 1.2-million placeholders.

DBI version 1.650 sets a hard limit of 99,999 placeholders.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14739
