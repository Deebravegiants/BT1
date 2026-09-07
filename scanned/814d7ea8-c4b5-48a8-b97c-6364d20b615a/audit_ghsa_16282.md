# [M] Apache Superset: Improper data authorization when creating a new dataset

## Summary
Severity: Medium
Advisory: GHSA-wr6g-9wcr-cmqj
CVE: CVE-2024-24779
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-wr6g-9wcr-cmqj
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.4
- PyPI: `apache-superset` — affected >=3.1.0 <3.1.1

## Details
Apache Superset with custom roles that include `can write on dataset` and without all data access permissions, allows for users to create virtual datasets to data they don't have access to. These users could then use those virtual datasets to get access to unauthorized data.
This issue affects Apache Superset: before 3.0.4, from 3.1.0 before 3.1.1.

Users are recommended to upgrade to version 3.1.1 or 3.0.4, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24779
- https://github.com/apache/superset
- https://lists.apache.org/thread/xzhz1m5bb9zxhyqgoy4q2d689b3zp4pq
- http://www.openwall.com/lists/oss-security/2024/02/28/6
