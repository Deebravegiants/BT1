# [H] SQL Injection in connect-pg-simple

## Summary
Severity: High
Advisory: GHSA-xqh8-5j36-4556
CVE: CVE-2019-15658
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-08-26
Source: https://github.com/advisories/GHSA-xqh8-5j36-4556
Type: github-advisory

## Affected
- npm: `connect-pg-simple` — affected >=0 <6.0.1

## Details
### Impact
An unlikely SQL injection if the case of an unsanitized table name input.

### Patches
The user should upgrade to `6.0.1`. Due to its low impact a backport has not been made to the `5.x` branch.

### Workarounds
If there is no likelihood that the `tableName` or `schemaName` options sent to the constructor could be of an unsanitized nature, then no workaround is needed. Else the input could be sanitized and escaped before sending it in. Take note though that such an escaping would need to be removed when upgrading to `6.0.1` or later, to avoid double escaping.

### References
* [Security issue disclosure](https://github.com/voxpelli/node-connect-pg-simple/issues/151)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [voxpelli/node-connect-pg-simple](https://github.com/voxpelli/node-connect-pg-simple)
* Email maintainer at [pelle@kodfabrik.se](mailto:pelle@kodfabrik.se)

## References
- https://github.com/voxpelli/node-connect-pg-simple/security/advisories/GHSA-xqh8-5j36-4556
- https://nvd.nist.gov/vuln/detail/CVE-2019-15658
- https://github.com/advisories/GHSA-xqh8-5j36-4556
- https://github.com/voxpelli/node-connect-pg-simple
- https://snyk.io/vuln/SNYK-JS-CONNECTPGSIMPLE-460154
- https://www.npmjs.com/advisories/1153
