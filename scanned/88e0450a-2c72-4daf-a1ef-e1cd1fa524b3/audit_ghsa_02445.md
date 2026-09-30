# [M] Missing Authorization in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-m6h2-jx9v-58w6
CVE: CVE-2021-35936
CWE: CWE-306, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-m6h2-jx9v-58w6
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.1.2

## Details
If remote logging is not used, the worker (in the case of CeleryExecutor) or the scheduler (in the case of LocalExecutor) runs a Flask logging server and is listening on a specific port and also binds on 0.0.0.0 by default. This logging server had no authentication and allows reading log files of DAG jobs. This issue affects Apache Airflow < 2.1.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-35936
- https://github.com/apache/airflow/commit/27265516d2b897585f5019ecd820cfe5471fd351
- https://github.com/apache/airflow/commit/7a5bb88ad78d600fbb1676a55752597928115bd8
- https://github.com/apache/airflow/commit/d772f38f843b9add5319a01cf51a844145b01f63
- https://github.com/advisories/GHSA-m6h2-jx9v-58w6
- https://github.com/apache/airflow
- https://github.com/apache/airflow/compare/2.1.1...2.1.2
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2021-122.yaml
- https://lists.apache.org/thread.html/r53d6bd7b0a66f92ddaf1313282f10fec802e71246606dd30c16536df%40%3Cusers.airflow.apache.org%3E
