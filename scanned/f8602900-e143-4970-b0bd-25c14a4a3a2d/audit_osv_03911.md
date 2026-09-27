# [H] ALPINE-CVE-2026-6464

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6464
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6464
Type: osv

## Affected
- Alpine:v3.21: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
Untrusted data inclusion in PostgreSQL psql COPY may allow a server administrator to elicit execution of data lines as psql commands, via error injection.  If the "COPY FROM STDIN" or "\copy FROM STDIN" command fails before the server indicates that it awaits input rows, psql processes the in-line data rows as psql commands.  "COPY FROM" with a filename is unaffected.  The server administrator has no inherent control over the data rows, so a complete attack requires the attacker to separately acquire control of both the server and the data rows.  Alternatively, an attacker controlling data rows alone might complete an attack through a coincidental error that they don't control.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6464
