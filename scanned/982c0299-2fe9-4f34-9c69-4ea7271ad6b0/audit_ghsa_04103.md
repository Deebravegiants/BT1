# [H] SQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-2777-2vq8-c4v4
CVE: CVE-2019-11069
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-04-11
Source: https://github.com/advisories/GHSA-2777-2vq8-c4v4
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=5.0.0 <5.3.0

## Details
Versions of `sequelize` prior to 5.3.0 (excluding v3 and v4) are vulnerable to SQL Injection. PostgreSQL option`standard_conforming_strings` is not set to `on` by default, which may allow attackers to inject SQL statements due to poor handling of backslashes in string literals.


## Recommendation

Upgrade to version 5.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11069
- https://github.com/sequelize/sequelize/pull/10746
- https://github.com/sequelize/sequelize/pull/10746/files
- https://github.com/sequelize/sequelize/commit/850c7fd04669e0fef9238b6dc4f8d6ee93ed71e9
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/blob/98cb17c17f73e2aa1792aa5a1d31216ba984b456/lib/dialects/postgres/connection-manager.js#L158-L160
- https://github.com/sequelize/sequelize/releases/tag/v5.3.0
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-174167
