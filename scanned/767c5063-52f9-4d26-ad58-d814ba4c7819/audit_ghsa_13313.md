# [M] Apache Superset vulnerable to Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-cmjc-52fg-9f7j
CVE: CVE-2023-30776
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-cmjc-52fg-9f7j
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=1.3.0 <2.1.0

## Details
An authenticated user with specific data permissions could access database connections stored passwords by requesting a specific REST API. This issue affects Apache Superset version 1.3.0 up to 2.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30776
- https://github.com/apache/superset
- https://lists.apache.org/thread/s9w9w10mt2sngk3solwnmq5k7md53tsz
- http://www.openwall.com/lists/oss-security/2023/04/24/3
