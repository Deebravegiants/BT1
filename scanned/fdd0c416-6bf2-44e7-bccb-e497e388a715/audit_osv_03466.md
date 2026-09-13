# [C] ALPINE-CVE-2026-15043

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-15043
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-15043
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI::SQL::Nano versions from 1.42 before 1.651 for Perl have inverted <= and >= SQL operators on text.

DBI::SQL::Nano, DBI's built-in mini-SQL engine, evaluated WHERE predicates incorrectly in some cases. In the non-numeric string branch of the is_matched method, <= was evaluated using Perl's ge operator, and >= was evaluated using Perl's le operator.

SQL::Nano is the fallback query engine for DBI's file-backed drivers (DBD::File, DBD::DBM, CSV-style drivers) whenever SQL::Statement is not installed, and is forced whenever DBI_SQL_NANO=1. Queries over such tables use these predicates directly.

The impact depends on the context. Where an application relies on a WHERE clause to filter file-backed data for policy or authorization, an inverted <=/>= comparison silently returns the wrong rows.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-15043
