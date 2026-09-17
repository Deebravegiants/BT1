# [H] ALPINE-CVE-2026-6637

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6637
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6637
Type: osv

## Affected
- Alpine:v3.20: `postgresql15` — affected >=0 <15.18-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
Stack buffer overflow in PostgreSQL module "refint" allows an unprivileged database user to execute arbitrary code as the operating system user running the database.  A distinct attack is possible if the application declares a user-controlled column as a "refint" cascade primary key and facilitates user-controlled updates to that column.  In that case, a SQL injection allows a primary key update value provider to execute arbitrary SQL as the database user performing the primary key update.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6637
