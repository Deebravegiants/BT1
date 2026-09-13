# [H] ALPINE-CVE-2026-15392

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-15392
Ecosystem: Alpine:v3.24
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-15392
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBD::File versions before 1.651 for Perl do not ensure the table file is not a symlink to an untrusted location.

The complete_table_name method builds the absolute table file path without checking whether the file is a symbolic link. A link inside the data directory can point to a table file at any path outside of the configured f_dir and f_dir_search directories.

Callers of file-based drivers can read or write files outside of the data directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-15392
