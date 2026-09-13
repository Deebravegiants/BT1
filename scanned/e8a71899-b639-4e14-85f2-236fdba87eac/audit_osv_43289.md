# [C] DBI versions before 1.652 for Perl allow a heap out-of-bounds write via an unvalidated numeric placeholder that sets the binder counter in preparse

## Summary
Severity: Critical
Advisory: CVE-2026-73194
Aliases: GHSA-623j-hfpc-mrc4
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-73194
Type: osv

## Details
DBI versions before 1.652 for Perl allow a heap out-of-bounds write via an unvalidated numeric placeholder that sets the binder counter in preparse.

preparse reserves seven output bytes per input byte, the width of the longest ':p99999' expansion. The ':N' branch parses the number with `atoi(src)` and assigns it to the binder counter with no range check, so a statement containing ':2147483648' leaves the counter negative (-2147483648 with glibc, where atoi wraps). Each following '?' then expands through `sprintf(start, ":p%d", idx++)` to ':p-2147483648', 14 bytes with the terminating NUL where the buffer budgets 7. The placeholder limit added in 1.650 tests the counter against 99,999, which a negative counter passes.

Any caller that preparses an untrusted statement into ':pN' style placeholders gets a heap out-of-bounds write that grows with the number of '?' marks following the poisoned placeholder. The '?' and '%s' return styles compare the parsed number against the expected sequence and error out, and are unaffected.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-10879
- https://www.cve.org/CVERecord?id=CVE-2026-14739
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73194.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-623j-hfpc-mrc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-73194
- https://github.com/perl5-dbi/dbi/commit/29b72ae7d2a8114a734a55840bf1c45b89207809.patch
- https://github.com/perl5-dbi/dbi
