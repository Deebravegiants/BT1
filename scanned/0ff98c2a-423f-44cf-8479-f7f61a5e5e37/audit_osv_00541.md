# [H] ALPINE-CVE-2017-15286

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15286
Ecosystem: Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15286
Type: osv

## Affected
- Alpine:v3.6: `sqlite` — affected >=0 <3.20.1-r1

## Details
SQLite 3.20.1 has a NULL pointer dereference in tableColumnList in shell.c because it fails to consider certain cases where `sqlite3_step(pStmt)==SQLITE_ROW` is false and a data structure is never initialized.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15286
