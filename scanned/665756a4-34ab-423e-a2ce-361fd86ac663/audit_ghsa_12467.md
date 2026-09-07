# [M] Apache Airflow Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6m9r-7wrx-xmr6
CVE: CVE-2023-49920
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-6m9r-7wrx-xmr6
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.7.0 <2.8.0

## Details
Apache Airflow, version 2.7.0 through 2.7.3, has a vulnerability that allows an attacker to trigger a DAG in a GET request without CSRF validation. As a result, it was possible for a malicious website opened in the same browser - by the user who also had Airflow UI opened - to trigger the execution of DAGs without the user's consent.
Users are advised to upgrade to version 2.8.0 or later which is not affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49920
- https://github.com/apache/airflow/pull/36026
- https://github.com/apache/airflow/commit/f5d802791fa5f6b13b635f06a1ea2eccc22a9ba7
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-266.yaml
- https://lists.apache.org/thread/mnwd2vcfw3gms6ft6kl951vfbqrxsnjq
- http://www.openwall.com/lists/oss-security/2023/12/21/3
