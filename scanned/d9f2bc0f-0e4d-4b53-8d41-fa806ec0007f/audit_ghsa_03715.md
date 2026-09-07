# [H] Improper Certificate Validation in Apache Airflow

## Summary
Severity: High
Advisory: GHSA-77rc-x84q-pv4f
CVE: CVE-2018-20245
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-01-25
Source: https://github.com/advisories/GHSA-77rc-x84q-pv4f
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.1

## Details
The LDAP auth backend (airflow.contrib.auth.backends.ldap_auth) prior to Apache Airflow 1.10.1 was misconfigured and contained improper checking of exceptions which disabled server certificate checking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20245
- https://github.com/apache/airflow/commit/28abf87bd173cc4cedc57f553118470e5745a968
- https://github.com/apache/airflow/commit/66d0d05ea0802aec407e0ef5435a962080db0926
- https://github.com/apache/airflow/commit/d8d0e8c59203f793f81d47d5adb1362df0b5d8d1
- https://github.com/advisories/GHSA-77rc-x84q-pv4f
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2019-143.yaml
- https://lists.apache.org/thread.html/b549c7573b342a6e457e5a3225c33054244343927bbfb2a4cdc4cf73@%3Cdev.airflow.apache.org%3E
