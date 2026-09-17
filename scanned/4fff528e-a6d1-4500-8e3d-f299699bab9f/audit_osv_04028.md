# [H] Apache Airflow: Authenticated DAG authors could execute code on scheduler nodes

## Summary
Severity: High
Advisory: BIT-airflow-2024-45034
Aliases: CVE-2024-45034, GHSA-92xg-gmrq-5c3w, PYSEC-2024-212
Ecosystem: Bitnami
Published: 2024-09-10
Source: https://osv.dev/vulnerability/BIT-airflow-2024-45034
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.10.1

## Details
Apache Airflow versions before 2.10.1 have a vulnerability that allows DAG authors to add local settings to the DAG folder and get it executed by the scheduler, where the scheduler is not supposed to execute code submitted by the DAG author. 
Users are advised to upgrade to version 2.10.1 or later, which has fixed the vulnerability.

## References
- https://github.com/apache/airflow/pull/41672
- https://lists.apache.org/thread/b4fcw33vh60yfg9990n5vmc7sy2dcgjx
- http://www.openwall.com/lists/oss-security/2024/09/06/3
- https://nvd.nist.gov/vuln/detail/CVE-2024-45034
