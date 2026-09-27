# [C] DBI versions before 1.650 for Perl have a heap overflow when preparsing SQL statements with an extreme number of placeholders

## Summary
Severity: Critical
Advisory: CVE-2026-14739
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-14739
Type: osv

## Details
DBI versions before 1.650 for Perl have a heap overflow when preparsing SQL statements with an extreme number of placeholders.

The fix for CVE-2026-10879 did not allocate enough memory to handle approximately 1.2-million placeholders.

DBI version 1.650 sets a hard limit of 99,999 placeholders.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14739.json
- https://metacpan.org/release/HMBRAND/DBI-1.650/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14739
- https://www.cve.org/CVERecord?id=CVE-2026-10879
- https://github.com/perl5-dbi/dbi/commit/2b77c88b655e9539a592c71a61fb965fc0075395.patch
- https://github.com/perl5-dbi/dbi
