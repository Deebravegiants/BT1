# [C] ALPINE-CVE-2026-10879

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-10879
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-10879
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.648-r0

## Details
DBI versions before 1.648 for Perl have a heap overflow when preparsing SQL statements with more than 9 binders.

The preparse method expands SQL placeholder characters to numbered binders of the form :pN, but only allocates three characters per binder in the buffer.  Placeholders 10-99 require four characters, 100-999 require five characters, et cetera.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-10879
