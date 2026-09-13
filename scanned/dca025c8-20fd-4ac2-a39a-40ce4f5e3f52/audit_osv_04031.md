# [C] Apache Airflow: DAG author RCE on webserver via unrestricted import_string() in BaseSerialization.deserialize()

## Summary
Severity: Critical
Advisory: BIT-airflow-2026-33264
Aliases: CVE-2026-33264, GHSA-2943-9672-r45w, PYSEC-2026-2082
Ecosystem: Bitnami
Published: 2026-07-09
Source: https://osv.dev/vulnerability/BIT-airflow-2026-33264
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.0

## Details
A bug in `BaseSerialization.deserialize()` allowed unrestricted `import_string()` of attacker-controlled class paths when the Scheduler / API Server loaded a serialized DAG: a DAG author could embed a malicious trigger into a DAG to gain remote code execution on the API Server / Scheduler process, crossing the Airflow security boundary that DAG-author code must never execute in those processes. Users are advised to upgrade to `apache-airflow` 3.3.0 or later. As a defense-in-depth mitigation, deployments where DAG-author trust is limited can restrict the `[core] allowed_deserialization_classes` config to a narrow allowlist.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/1
- https://github.com/apache/airflow/pull/66002
- https://github.com/apache/airflow/pull/68528
- https://lists.apache.org/thread/otvdw8qt2y7xy2n5nq9xby9ky4rf5ltj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33264
