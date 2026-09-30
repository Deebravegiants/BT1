# [M] Apache Superset users may incorrectly create resources using the import charts feature 

## Summary
Severity: Medium
Advisory: GHSA-9qc3-p9jq-2x27
CVE: CVE-2023-27526
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-9qc3-p9jq-2x27
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
A non Admin authenticated user could incorrectly create resources using the import charts feature, on Apache Superset up to and including 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27526
- https://github.com/apache/superset
- https://lists.apache.org/thread/ndww89yl2jd98lvn23n9cj722lfdg8dv
