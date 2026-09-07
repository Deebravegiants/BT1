# [M] Parse Server has a SQL injection via query field name when using PostgreSQL

## Summary
Severity: Medium
Advisory: GHSA-c442-97qw-j6c6
CVE: CVE-2026-32234
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:L/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-c442-97qw-j6c6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.10
- npm: `parse-server` — affected >=0 <8.6.36

## Details
### Impact

An attacker with access to the master key can inject malicious SQL via crafted field names used in query constraints when Parse Server is configured with PostgreSQL as the database. The field name in a `$regex` query operator is passed to PostgreSQL using unparameterized string interpolation, allowing the attacker to manipulate the SQL query. While the master key controls what can be done through the Parse Server abstraction layer, this SQL injection bypasses Parse Server entirely and operates at the database level.

This vulnerability only affects Parse Server deployments using PostgreSQL.

### Patches

The fix applies proper SQL identifier escaping to field names in the query handler and hardens query field name validation to reject malicious field names for all query types.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-c442-97qw-j6c6
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.10
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.36

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-c442-97qw-j6c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32234
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.36
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.10
