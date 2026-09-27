# [C] DBI versions before 1.650 for Perl read one byte out-of-bounds in preparse when deleting an initial SQL comment

## Summary
Severity: Critical
Advisory: CVE-2026-14740
Aliases: GHSA-35f4-f8m9-w8xg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-14740
Type: osv

## Details
DBI versions before 1.650 for Perl read one byte out-of-bounds in preparse when deleting an initial SQL comment.

The preparse method normalises SQL and removes comments. When the SQL starts with a comment line, the deletion of that line during normalisation led to an out-of-bounds read by one byte. The result is a fault on memory-hardened builds and nondeterministic newline retention on normal builds.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/17
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14740.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-35f4-f8m9-w8xg
- https://metacpan.org/release/HMBRAND/DBI-1.650/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14740
- https://github.com/perl5-dbi/dbi/commit/fc16f9e8b3dd5c65caf1867781ab2bfe2fadcc01.patch
- https://github.com/perl5-dbi/dbi
