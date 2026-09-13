# [M] Apache Airflow Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5938-79hg-xh3q
CVE: CVE-2023-50783
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-5938-79hg-xh3q
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.8.0

## Details
Apache Airflow, versions before 2.8.0, is affected by a vulnerability that allows an authenticated user without the variable edit permission, to update a variable.
This flaw compromises the integrity of variable management, potentially leading to unauthorized data modification.
Users are recommended to upgrade to 2.8.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50783
- https://github.com/apache/airflow/pull/33932
- https://github.com/apache/airflow/commit/0e1c106d7cd0703125528a691088e42e17c99929
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-267.yaml
- https://lists.apache.org/thread/rs7cr3yp726mb89s1m844hy9pq7frgcn
- http://www.openwall.com/lists/oss-security/2023/12/21/4
