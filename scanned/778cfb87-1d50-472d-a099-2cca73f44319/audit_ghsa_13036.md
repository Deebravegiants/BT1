# [H] Apache Airflow Execution with Unnecessary Privileges

## Summary
Severity: High
Advisory: GHSA-269x-pg5c-5xgm
CVE: CVE-2023-39508
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-05
Source: https://github.com/advisories/GHSA-269x-pg5c-5xgm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.6.0b1

## Details
Execution with Unnecessary Privileges, : Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Software Foundation Apache Airflow.The "Run Task" feature enables authenticated user to bypass some of the restrictions put in place. It allows to execute code in the webserver context as well as allows to bypas limitation of access the user has to certain DAGs. The "Run Task" feature is considered dangerous and it has been removed entirely in Airflow 2.6.0.

This issue affects Apache Airflow: before 2.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39508
- https://github.com/apache/airflow/pull/29706
- https://github.com/apache/airflow/commit/101d59c4b88ab979d305b8d96f612c27c8a44aa8
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-134.yaml
- https://lists.apache.org/thread/j2nkjd0zqvtqk85s6ywpx3c35pvzyx15
- http://seclists.org/fulldisclosure/2023/Jul/43
