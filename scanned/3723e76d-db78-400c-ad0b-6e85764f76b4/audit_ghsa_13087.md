# [H] Apache Airflow vulnerable arbitrary code execution via Spark server

## Summary
Severity: High
Advisory: GHSA-8q28-pw9g-w82c
CVE: CVE-2023-40195
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-28
Source: https://github.com/advisories/GHSA-8q28-pw9g-w82c
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-spark` — affected >=0 <4.1.3

## Details
Deserialization of Untrusted Data, Inclusion of Functionality from Untrusted Control Sphere vulnerability in Apache Software Foundation Apache Airflow Spark Provider.

When the Apache Spark provider is installed on an Airflow deployment, an Airflow user that is authorized to configure Spark hooks can effectively run arbitrary code on the Airflow node by pointing it at a malicious Spark server. Prior to version 4.1.3, this was not called out in the documentation explicitly, so it is possible that administrators provided authorizations to configure Spark hooks without taking this into account. We recommend administrators to review their configurations to make sure the authorization to configure Spark hooks is only provided to fully trusted users.

To view the warning in the docs please visit  https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/4.1.3/connections/spark.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40195
- https://github.com/apache/airflow/pull/33233
- https://github.com/apache/airflow/commit/6850b5c777fa515e110ad1daa85242209a8ec6c0
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-apache-spark/PYSEC-2023-156.yaml
- https://lists.apache.org/thread/fzy95b1d6zv31j5wrx3znhzcscck2o24
