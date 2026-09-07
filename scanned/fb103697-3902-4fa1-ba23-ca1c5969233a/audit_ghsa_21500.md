# [H] Apache Airflow vulnerable to OS Command Injection via example DAGs

## Summary
Severity: High
Advisory: GHSA-6pw3-8h9w-32gc
CVE: CVE-2022-40127
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-14
Source: https://github.com/advisories/GHSA-6pw3-8h9w-32gc
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.4.0

## Details
A vulnerability in Example Dags of Apache Airflow allows an attacker with UI access who can trigger DAGs, to execute arbitrary commands via manually provided run_id parameter. This issue affects Apache Airflow versions prior to 2.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40127
- https://github.com/apache/airflow/pull/25960
- https://github.com/apache/airflow/commit/372e699c2d1e11f7087b5340454d0a0a6a56fbf5
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2022-42982.yaml
- https://lists.apache.org/thread/cf132hgm6jvzvsbpsozl3plf1r4cwysy
- http://www.openwall.com/lists/oss-security/2022/11/14/2
