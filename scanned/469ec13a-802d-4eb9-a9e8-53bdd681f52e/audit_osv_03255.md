# [M] ALPINE-CVE-2025-29088

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-29088
Ecosystem: Alpine:v3.21
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-29088
Type: osv

## Affected
- Alpine:v3.21: `sqlite` — affected >=0 <3.48.0-r4

## Details
In SQLite 3.49.0 before 3.49.1, certain argument values to sqlite3_db_config (in the C-language API) can cause a denial of service (application crash). An sz*nBig multiplication is not cast to a 64-bit integer, and consequently some memory allocations may be incorrect.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-29088
