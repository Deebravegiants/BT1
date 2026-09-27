# [H] JLSEC-2026-607

## Summary
Severity: High
Advisory: JLSEC-2026-607
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-607
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Stack buffer overflow in PostgreSQL module "refint" allows an unprivileged database user to execute arbitrary code as the operating system user running the database.  A distinct attack is possible if the application declares a user-controlled column as a "refint" cascade primary key and facilitates user-controlled updates to that column.  In that case, a SQL injection allows a primary key update value provider to execute arbitrary SQL as the database user performing the primary key update.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2026-6637/
