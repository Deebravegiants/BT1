# [M] Apache Superset SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jfxj-xf67-x723
CVE: CVE-2023-49736
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-jfxj-xf67-x723
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.3
- PyPI: `apache-superset` — affected >=3.0.0 <3.0.2

## Details
A where_in JINJA macro allows users to specify a quote, which combined with a carefully crafted statement would allow for SQL injection in Apache Superset.This issue affects Apache Superset: before 2.1.3, from 3.0.0 before 3.0.2.

Users are recommended to upgrade to version 2.1.3 or 3.0.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49736
- https://github.com/apache/superset/pull/25779
- https://github.com/apache/superset/commit/1d403dab9822a8cee6108669c53e53fad881c751
- https://github.com/apache/superset/commit/34101594e284ab3acce692f41aff7759ccb4bf1d
- https://github.com/apache/superset
- https://lists.apache.org/thread/1kf481bgs3451qcz6hfhobs7xvhp8n1p
- http://www.openwall.com/lists/oss-security/2023/12/19/2
