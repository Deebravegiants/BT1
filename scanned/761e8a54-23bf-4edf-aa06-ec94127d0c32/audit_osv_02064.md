# [M] ALPINE-CVE-2021-20229

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-20229
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20229
Type: osv

## Affected
- Alpine:v3.12: `postgresql` — affected >=13.0 <12.6-r0
- Alpine:v3.13: `postgresql` — affected >=13.0 <13.2-r0
- Alpine:v3.14: `postgresql` — affected >=13.0 <13.2-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.2-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.2-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <13.2-r0

## Details
A flaw was found in PostgreSQL in versions before 13.2. This flaw allows a user with SELECT privilege on one column to craft a special query that returns all columns of the table. The highest threat from this vulnerability is to confidentiality.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20229
