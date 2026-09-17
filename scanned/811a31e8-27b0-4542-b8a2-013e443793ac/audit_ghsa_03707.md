# [H] sqla-yaml-fixtures is vulnerable to Code Injection

## Summary
Severity: High
Advisory: GHSA-2x54-j4m3-r6wx
CVE: CVE-2019-3575
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-2x54-j4m3-r6wx
Type: github-advisory

## Affected
- PyPI: `sqla-yaml-fixtures` — affected >=0

## Details
Sqla_yaml_fixtures versions up to 0.9.1 allows local users to execute arbitrary python code via the fixture_text argument in `sqla_yaml_fixtures.load`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3575
- https://github.com/schettino72/sqla_yaml_fixtures/issues/20
- https://github.com/advisories/GHSA-2x54-j4m3-r6wx
- https://github.com/pypa/advisory-database/tree/main/vulns/sqla-yaml-fixtures/PYSEC-2019-122.yaml
- https://github.com/schettino72/sqla_yaml_fixtures
