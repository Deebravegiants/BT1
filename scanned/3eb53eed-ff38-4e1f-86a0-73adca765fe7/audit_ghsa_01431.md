# [C] SQL Injection via GeoJSON in sequelize

## Summary
Severity: Critical
Advisory: GHSA-5v9h-q3gj-c32x
CVE: CVE-2016-1000225
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-5v9h-q3gj-c32x
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=3.4.0 <3.23.6

## Details
Affected versions of `sequelize` are vulnerable to SQL Injection in Models that have fields with the `GEOMETRY` DataType. This vulnerability occurs because single quotes in document values are not escaped for GeoJSON documents using `ST_GeomFromGeoJSON`, and MySQL GeoJSON documents using `GeomFromText`.


## Recommendation

Update to version 3.23.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000225
- https://github.com/sequelize/sequelize/issues/6194
- https://github.com/sequelize/sequelize/pull/6302
- https://github.com/sequelize/sequelize/pull/6306
- https://github.com/sequelize/sequelize/commit/14e3deaf3ad27f12900e5275db1d448844c9de3e
- https://github.com/sequelize/sequelize/commit/18ac91040d9c57351d26ba998f460e214255b704
- https://github.com/sequelize/sequelize/commit/562d52585902090f4e53eb21c61314098c29d795
- https://github.com/sequelize/sequelize/commit/f93af43a1d86400487f5e3d9762f1a4b7cf6b1e1
- https://github.com/sequelize/sequelize
- https://snyk.io/vuln/npm:sequelize:20160718
