# [C] DBI versions before 1.648 for Perl have a heap overflow when preparsing SQL statements with more than 9 binders

## Summary
Severity: Critical
Advisory: CVE-2026-10879
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-10879
Type: osv

## Details
DBI versions before 1.648 for Perl have a heap overflow when preparsing SQL statements with more than 9 binders.

The preparse method expands SQL placeholder characters to numbered binders of the form :pN, but only allocates three characters per binder in the buffer.  Placeholders 10-99 require four characters, 100-999 require five characters, et cetera.

## References
- http://www.openwall.com/lists/oss-security/2026/06/06/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10879.json
- https://metacpan.org/release/HMBRAND/DBI-1.648/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-10879
- https://github.com/perl5-dbi/dbi/commit/af79036c07aa9a457971c0f4136e37c85dc20978.patch
- https://github.com/perl5-dbi/dbi
