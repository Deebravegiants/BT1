# [C] DBI versions before 1.651 for Perl do not enforce statement handle consistency with the row

## Summary
Severity: Critical
Advisory: CVE-2026-60082
Aliases: GHSA-rwhc-hhmv-cjvg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-60082
Type: osv

## Details
DBI versions before 1.651 for Perl do not enforce statement handle consistency with the row.

When the statement handle had no fields but the source row was non-empty, the internal row-buffer helper would read from a negative array index.

This could be triggered by a caller supplying inconsistent metadata and rows to the prepare method.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/13
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60082.json
- https://github.com/perl5-dbi/dbi/security/advisories/GHSA-rwhc-hhmv-cjvg
- https://metacpan.org/release/HMBRAND/DBI-1.651/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-60082
- https://github.com/perl5-dbi/dbi/commit/397868704291bbf0989b97e2c0661189890653e2.patch
- https://github.com/perl5-dbi/dbi
