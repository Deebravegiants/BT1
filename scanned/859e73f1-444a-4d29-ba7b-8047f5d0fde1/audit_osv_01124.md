# [H] ALPINE-CVE-2018-20346

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20346
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20346
Type: osv

## Affected
- Alpine:v3.6: `sqlite` — affected >=0 <3.25.3-r0
- Alpine:v3.7: `sqlite` — affected >=0 <3.25.3-r0
- Alpine:v3.8: `sqlite` — affected >=0 <3.25.3-r0

## Details
SQLite before 3.25.3, when the FTS3 extension is enabled, encounters an integer overflow (and resultant buffer overflow) for FTS3 queries that occur after crafted changes to FTS3 shadow tables, allowing remote attackers to execute arbitrary code by leveraging the ability to run arbitrary SQL statements (such as in certain WebSQL use cases), aka Magellan.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20346
