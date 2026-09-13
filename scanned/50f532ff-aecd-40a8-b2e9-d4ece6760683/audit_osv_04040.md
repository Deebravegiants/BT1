# [M] Apache Airflow: Task-instance API exposes secrets in deferred trigger kwargs

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-49487
Aliases: CVE-2026-49487, GHSA-22hf-vx2v-gjff, PYSEC-2026-2088
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-airflow-2026-49487
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.0

## Details
In Apache Airflow before 3.3.0, the REST API task-instance detail and list
endpoints returned a deferred task's trigger kwargs without masking. When a
deferred operator passed a secret (for example a provider API key) into its
trigger, any authenticated user with DAG-scoped task-instance read access for
that DAG could read that secret in clear text while the task was deferred.
Users should upgrade to apache-airflow 3.3.0 or later, which masks sensitive
values in trigger kwargs returned by the API.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/6
- https://github.com/apache/airflow/pull/67868
- https://lists.apache.org/thread/qlw6pozlzlfhkvmbgqsbjlq6vj4v0pc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-49487
