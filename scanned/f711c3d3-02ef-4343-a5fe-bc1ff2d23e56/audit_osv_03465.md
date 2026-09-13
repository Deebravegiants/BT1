# [C] ALPINE-CVE-2026-14740

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-14740
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14740
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI versions before 1.650 for Perl read one byte out-of-bounds in preparse when deleting an initial SQL comment.

The preparse method normalises SQL and removes comments. When the SQL starts with a comment line, the deletion of that line during normalisation led to an out-of-bounds read by one byte. The result is a fault on memory-hardened builds and nondeterministic newline retention on normal builds.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14740
