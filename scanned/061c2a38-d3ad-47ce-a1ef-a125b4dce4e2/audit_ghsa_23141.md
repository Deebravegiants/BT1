# [H] Apache Superset allowed for database connections password leak for authenticated users

## Summary
Severity: High
Advisory: GHSA-42q4-9xf9-f67x
CVE: CVE-2021-41972
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-42q4-9xf9-f67x
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <1.3.2

## Details
Apache Superset up to and including 1.3.1 allowed for database connections password leak for authenticated users. This information could be accessed in a non-trivial way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41972
- https://github.com/advisories/GHSA-42q4-9xf9-f67x
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2021-434.yaml
- https://lists.apache.org/thread/xpdl2r538o695o7r9gd9qrwqb17bdd3v
- https://seclists.org/oss-sec/2021/q4/106
