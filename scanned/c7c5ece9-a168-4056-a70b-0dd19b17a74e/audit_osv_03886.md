# [C] ALPINE-CVE-2026-60082

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-60082
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-60082
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI versions before 1.651 for Perl do not enforce statement handle consistency with the row.

When the statement handle had no fields but the source row was non-empty, the internal row-buffer helper would read from a negative array index.

This could be triggered by a caller supplying inconsistent metadata and rows to the prepare method.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-60082
