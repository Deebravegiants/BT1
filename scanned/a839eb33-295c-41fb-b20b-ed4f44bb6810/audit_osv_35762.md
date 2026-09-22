# [C] DBIx::QuickORM versions before 0.000026 for Perl allow SQL injection via unquoted SQL identifiers

## Summary
Severity: Critical
Advisory: CVE-2026-13766
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-13766
Type: osv

## Details
DBIx::QuickORM versions before 0.000026 for Perl allow SQL injection via unquoted SQL identifiers.

The default SQL builder, a SQL::Abstract subclass, sets bindtype in its constructor but never quote_char, so SQL::Abstract emits identifiers verbatim. Caller-supplied identifiers (order_by, where-clause column keys, field and returning lists, upsert columns, and join aliases) reach the SQL string raw, while values are placeholder-bound and unaffected.

A caller that forwards untrusted input to an affected identifier position, such as a user-controlled order_by value, enables SQL injection: the row order can be made to depend on a sub-select over columns the query never selected, and the where and update identifier positions permit further data disclosure and tampering.

## References
- http://www.openwall.com/lists/oss-security/2026/06/30/4
- https://cpan.org/modules
- https://github.com/exodist/DBIx-QuickORM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13766.json
- https://metacpan.org/release/EXODIST/DBIx-QuickORM-0.000026/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13766
- https://github.com/exodist/DBIx-QuickORM/commit/43d7684682050780f056f25e1879191fb0a3265e.patch
