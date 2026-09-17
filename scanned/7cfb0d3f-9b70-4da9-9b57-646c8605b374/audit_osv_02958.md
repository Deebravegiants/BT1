# [H] ALPINE-CVE-2023-7104

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-7104
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-7104
Type: osv

## Affected
- Alpine:v3.16: `sqlite` — affected >=0 <3.40.1-r1
- Alpine:v3.17: `sqlite` — affected >=0 <3.40.1-r1
- Alpine:v3.18: `sqlite` — affected >=0 <3.41.2-r3

## Details
A vulnerability was found in SQLite SQLite3 up to 3.43.0 and classified as critical. This issue affects the function sessionReadRecord of the file ext/session/sqlite3session.c of the component make alltest Handler. The manipulation leads to heap-based buffer overflow. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-248999.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-7104
