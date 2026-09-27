# [C] DBI versions before 1.652 for Perl allow a heap out-of-bounds write on 32-bit perl via an integer wraparound in the output buffer size computed by preparse

## Summary
Severity: Critical
Advisory: CVE-2026-73193
Aliases: GHSA-wj3v-c3hh-mhqr
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-73193
Type: osv

## Details
DBI versions before 1.652 for Perl allow a heap out-of-bounds write on 32-bit perl via an integer wraparound in the output buffer size computed by preparse.

preparse reserves its output buffer with `newSV(strlen(statement) * 7 + 16)`, budgeting seven output bytes per input byte for the longest ':p99999' expansion. The product is computed in STRLEN, which is 32 bits wide on a 32-bit perl build, so a statement of 613,566,757 bytes multiplies to 4,294,967,299, wraps modulo 2^32 to 3, and reserves 19 bytes. The parser then copies the statement out through a raw pointer with no capacity check, writing the whole 585 MB input past the end of the allocation. The 99,999 placeholder limit does not bound this path, which is reached by ordinary non-placeholder content.

Any caller that passes an untrusted statement of that length to preparse on a 32-bit perl gets a heap out-of-bounds write of attacker controlled bytes. Builds with a 64-bit STRLEN are not affected, since the wrap there needs a statement of about 2.3 exabytes.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-14739
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73193.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-wj3v-c3hh-mhqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-73193
- https://github.com/perl5-dbi/dbi/commit/c751ae5a5a6f56c2f8284f37c1f4d43500352ef1.patch
- https://github.com/perl5-dbi/dbi
