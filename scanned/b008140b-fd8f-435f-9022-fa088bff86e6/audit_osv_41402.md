# [H] DBI::ProfileData versions before 1.651 for Perl do not limit the path index

## Summary
Severity: High
Advisory: CVE-2026-60081
Aliases: GHSA-ww49-w4mv-jrr4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-60081
Type: osv

## Details
DBI::ProfileData versions before 1.651 for Perl do not limit the path index.

The path index column of profile dump files is used to allocate an array of data for the parser. An unbounded value allows an attacker to specify a large index and consume available memory.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/14
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60081.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-ww49-w4mv-jrr4
- https://metacpan.org/release/HMBRAND/DBI-1.651/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-60081
- https://github.com/perl5-dbi/dbi/commit/6764e755e83ee1ebb1b40760e5b53eb50960bd7a.patch
- https://github.com/perl5-dbi/dbi
