# [H] Plaintext password leak in Apache Superset

## Summary
Severity: High
Advisory: GHSA-77pw-c3j2-5fc8
CVE: CVE-2020-13952
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-77pw-c3j2-5fc8
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <0.37.2

## Details
In the course of work on the open source project it was discovered that authenticated users running queries against Hive and Presto database engines could access information via a number of templated fields including the contents of query description metadata database, the hashed version of the authenticated users’ password, and access to connection information including the plaintext password for the current connection. It would also be possible to run arbitrary methods on the database connection object for the Presto or Hive connection, allowing the user to bypass security controls internal to Superset. This vulnerability is present in every Apache Superset version < 0.37.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13952
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2020-223.yaml
- https://lists.apache.org/thread.html/rf1faa368f580d2cb691576bee1277855f769667f3114d5df1dacbea6%40%3Cdev.superset.apache.org%3E
