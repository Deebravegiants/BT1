# [M] ALPINE-CVE-2020-15358

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15358
Ecosystem: Alpine:v3.12
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15358
Type: osv

## Affected
- Alpine:v3.12: `sqlite` — affected >=0 <3.32.1-r1

## Details
In SQLite before 3.32.3, select.c mishandles query-flattener optimization, leading to a multiSelectOrderBy heap overflow because of misuse of transitive properties for constant propagation.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15358
