# [M] Apache Airflow CNCF Kubernetes provider, Apache Airflow: Kubernetes configuration file saved without encryption in the Metadata and logged as plain text in the Triggerer service

## Summary
Severity: Medium
Advisory: GHSA-mg2x-mggj-6955
CVE: CVE-2023-51702
CWE: CWE-312
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-mg2x-mggj-6955
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.3.0 <2.6.1
- PyPI: `apache-airflow-providers-cncf-kubernetes` — affected >=5.2.0 <7.0.0

## Details
Since version 5.2.0, when using deferrable mode with the path of a Kubernetes configuration file for authentication, the Airflow worker serializes this configuration file as a dictionary and sends it to the triggerer by storing it in metadata without any encryption. Additionally, if used with an Airflow version between 2.3.0 and 2.6.0, the configuration dictionary will be logged as plain text in the triggerer service without masking. This allows anyone with access to the metadata or triggerer log to obtain the configuration file and use it to access the Kubernetes cluster.

This behavior was changed in version 7.0.0, which stopped serializing the file contents and started providing the file path instead to read the contents into the trigger. Users are recommended to upgrade to version 7.0.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51702
- https://github.com/apache/airflow/pull/29498
- https://github.com/apache/airflow/pull/30110
- https://github.com/apache/airflow/pull/36492
- https://github.com/apache/airflow
- https://lists.apache.org/thread/89x3q6lz5pykrkr1fkr04k4rfn9pvnv9
- http://www.openwall.com/lists/oss-security/2024/01/24/3
