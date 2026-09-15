# [H] ALPINE-CVE-2026-60081

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-60081
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-60081
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI::ProfileData versions before 1.651 for Perl do not limit the path index.

The path index column of profile dump files is used to allocate an array of data for the parser. An unbounded value allows an attacker to specify a large index and consume available memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-60081
