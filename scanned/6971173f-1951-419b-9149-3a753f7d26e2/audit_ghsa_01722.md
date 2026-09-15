# [M] SQL injection in Tortoise ORM

## Summary
Severity: Medium
Advisory: GHSA-9j2c-x8qm-qmjq
CVE: CVE-2020-11010
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-04-20
Source: https://github.com/advisories/GHSA-9j2c-x8qm-qmjq
Type: github-advisory

## Affected
- PyPI: `tortoise-orm` — affected >=0 <0.15.23
- PyPI: `tortoise-orm` — affected >=0.16.0 <0.16.6

## Details
### Impact
Various forms of SQL injection has been found, for MySQL and when filtering or doing mass-updates on char/text fields.
SQLite & PostgreSQL was only affected when filtering with ``contains``, ``starts_with`` or ``ends_with`` filters (and their case-insensitive counterparts)


### Patches
Please upgrade to 0.15.23+ or 0.16.6+

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Github](https://github.com/tortoise/tortoise-orm/issues)
* Chat to us on [Gitter](https://gitter.im/tortoise/community)

## References
- https://github.com/tortoise/tortoise-orm/security/advisories/GHSA-9j2c-x8qm-qmjq
- https://nvd.nist.gov/vuln/detail/CVE-2020-11010
- https://github.com/tortoise/tortoise-orm/commit/91c364053e0ddf77edc5442914c6f049512678b3
- https://github.com/pypa/advisory-database/tree/main/vulns/tortoise-orm/PYSEC-2020-144.yaml
- https://github.com/tortoise/tortoise-orm
