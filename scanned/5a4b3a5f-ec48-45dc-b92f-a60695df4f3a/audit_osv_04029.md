# [M] Apache Airflow: Secrets not masked in UI when sensitive variables are set via Airflow cli

## Summary
Severity: Medium
Advisory: BIT-airflow-2024-50378
Aliases: CVE-2024-50378, GHSA-j857-2pwm-jjmm, PYSEC-2026-1134
Ecosystem: Bitnami
Published: 2024-11-12
Source: https://osv.dev/vulnerability/BIT-airflow-2024-50378
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.10.3

## Details
Airflow versions before 2.10.3 have a vulnerability that allows authenticated users with audit log access to see sensitive values in audit logs which they should not see. When sensitive variables were set via airflow CLI, values of those variables appeared in the audit log and were stored unencrypted in the Airflow database. While this risk is limited to users with audit log access, it is recommended to upgrade to Airflow 2.10.3 or a later version, which addresses this issue. Users who previously used the CLI to set secret variables should manually delete entries with those variables from the log table.

## References
- https://github.com/apache/airflow/pull/43123
- https://lists.apache.org/thread/17rxys384lzfd6nhm3fztzgvk47zy7jb
- http://www.openwall.com/lists/oss-security/2024/11/08/5
- https://nvd.nist.gov/vuln/detail/CVE-2024-50378
