# [H] DBD::File versions before 1.651 for Perl do not ensure the table file is not a symlink to an untrusted location

## Summary
Severity: High
Advisory: CVE-2026-15392
Aliases: GHSA-mh3j-xwf4-jrqw
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15392
Type: osv

## Details
DBD::File versions before 1.651 for Perl do not ensure the table file is not a symlink to an untrusted location.

The complete_table_name method builds the absolute table file path without checking whether the file is a symbolic link. A link inside the data directory can point to a table file at any path outside of the configured f_dir and f_dir_search directories.

Callers of file-based drivers can read or write files outside of the data directory.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/15
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15392.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-mh3j-xwf4-jrqw
- https://metacpan.org/release/HMBRAND/DBI-1.651/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-15392
- https://github.com/perl5-dbi/dbi/commit/96d62dfe4528bf56fe13f413ed323d4252531728.patch
- https://github.com/perl5-dbi/dbi
