# [H] Apache Superset incorrect write permissions vulnerability

## Summary
Severity: High
Advisory: GHSA-g49j-j489-3xpf
CVE: CVE-2023-49734
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-g49j-j489-3xpf
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.3
- PyPI: `apache-superset` — affected >=3.0.0 <3.0.2

## Details
An authenticated Gamma user has the ability to create a dashboard and add charts to it, this user would automatically become one of the owners of the charts allowing him to incorrectly have write permissions to these charts.This issue affects Apache Superset: before 2.1.3, from 3.0.0 before 3.0.2.

Users are recommended to upgrade to version 3.0.2 or 2.1.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49734
- https://github.com/apache/superset/pull/25843
- https://github.com/apache/superset/commit/5198279a2ba41ab3e89bd9d7750694179d3f9fe6
- https://github.com/apache/superset/commit/cb6de0a9c9f505ee3f26e79ca9bfa5f3901528a0
- https://github.com/apache/superset
- https://lists.apache.org/thread/985h6ltvtbvdoysso780kkj7x744cds5
- http://www.openwall.com/lists/oss-security/2023/12/19/3
