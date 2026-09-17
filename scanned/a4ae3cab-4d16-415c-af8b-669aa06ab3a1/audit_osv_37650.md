# [C] UnQLite versions through 0.06 for Perl uses a potentially insecure version of the UnQLite library

## Summary
Severity: Critical
Advisory: CVE-2026-3257
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-3257
Type: osv

## Details
UnQLite versions through 0.06 for Perl uses a potentially insecure version of the UnQLite library.

UnQLite for Perl embeds the UnQLite library.  Version 0.06 and earlier of the Perl module uses a version of the library from 2014 that may be vulnerable to a heap-based overflow.

## References
- https://cpan.org/modules
- https://unqlite.symisc.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3257.json
- https://metacpan.org/release/TOKUHIROM/UnQLite-0.07/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-3257
- https://www.cve.org/CVERecord?id=CVE-2025-3791
- https://github.com/tokuhirom/UnQLite
