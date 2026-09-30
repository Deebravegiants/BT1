# [H] PgHero Allows Information Disclosure Through EXPLAIN Feature

## Summary
Severity: High
Advisory: GHSA-vf99-xw26-86g5
CVE: CVE-2023-22626
CWE: CWE-209
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-vf99-xw26-86g5
Type: github-advisory

## Affected
- RubyGems: `pghero` — affected >=0 <3.1.0

## Details
PgHero before 3.1.0 allows Information Disclosure via EXPLAIN because query results may be present in an error message. (Depending on database user privileges, this may only be information from the database, or may be information from file contents on the database server.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22626
- https://github.com/ankane/pghero/issues/439
- https://github.com/ankane/pghero
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pghero/CVE-2023-22626.yml
