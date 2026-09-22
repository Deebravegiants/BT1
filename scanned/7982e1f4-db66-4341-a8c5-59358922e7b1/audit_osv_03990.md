# [C] ALPINE-CVE-2026-9698

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-9698
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9698
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.648-r0

## Details
DBI versions before 1.648 for Perl saved errors in a limited-sized buffer.

Error messages that were returned when RaiseError, PrintError or HandleError were set were written to a 200-byte buffer without a length limit.

Attackers that can influence the error text in an application can trigger a buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9698
