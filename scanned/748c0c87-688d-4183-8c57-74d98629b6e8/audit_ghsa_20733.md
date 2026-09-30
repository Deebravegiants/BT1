# [C] loopback-connector-postgresql Vulnerable to Improper Sanitization of `contains` Filter

## Summary
Severity: Critical
Advisory: GHSA-j259-6c58-9m58
CVE: CVE-2022-35942
CWE: CWE-20, CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-j259-6c58-9m58
Type: github-advisory

## Affected
- npm: `loopback-connector-postgresql` — affected >=0 <5.5.1

## Details
Improper input validation on the `contains` LoopBack filter may allow for arbitrary SQL injection.

### Impact

When the extended filter property `contains` is permitted to be interpreted by the Postgres connector, it is possible to inject arbitrary SQL which may affect the confidentiality and integrity of data stored on the connected database.

This affects users who does any of the following:

- Connect to the database via the DataSource with `allowExtendedProperties: true` setting OR
- Uses the connector's CRUD methods directly OR
- Uses the connector's other methods to interpret the LoopBack filter.

### Patches

Patch release `loopback-connector-postgresql@5.5.1` has been published of which resolves this issue.

### Workarounds

Users who are unable to upgrade should do the following if applicable:

- Remove `allowExtendedProperties: true` DataSource setting
- Add `allowExtendedProperties: false` DataSource setting
- When passing directly to the connector functions, manually sanitize the user input for the `contains` LoopBack filter beforehand.

## References
- https://github.com/loopbackio/loopback-connector-postgresql/security/advisories/GHSA-j259-6c58-9m58
- https://nvd.nist.gov/vuln/detail/CVE-2022-35942
- https://github.com/loopbackio/loopback-connector-postgresql/commit/d57406c6737692a3a106b58a35406290cddb23e5
- https://github.com/loopbackio/loopback-connector-postgresql
