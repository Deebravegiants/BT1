# [H] Apache Airflow CNCF Kubernetes Provider: KubernetesPodOperator RCE via connection configuration

## Summary
Severity: High
Advisory: GHSA-2rx4-9f5h-9gjf
CVE: CVE-2023-33234
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-2rx4-9f5h-9gjf
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-cncf-kubernetes` — affected >=5.0.0 <7.0.0

## Details
Arbitrary code execution in Apache Airflow CNCF Kubernetes provider version 5.0.0 allows user to change xcom sidecar image and resources via Airflow connection.

In order to exploit this weakness, a user would already need elevated permissions (Op or Admin) to change the connection object in this manner. Operators should upgrade to provider version 7.0.0 which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33234
- https://github.com/apache/airflow
- https://lists.apache.org/thread/n1vpgl6h2qsdm52o9m2tx1oo86tl4gnq
