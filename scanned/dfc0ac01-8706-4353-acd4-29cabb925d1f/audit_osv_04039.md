# [M] Apache Airflow: Config API leaks per-key secrets backend kwargs - masker bypass on synthetic options

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-48892
Aliases: CVE-2026-48892, GHSA-9933-5rrp-mfwx, PYSEC-2026-2087
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-airflow-2026-48892
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.0

## Details
The Config API in Apache Airflow surfaced per-key secrets-backend overrides (environment variables like `AIRFLOW__SECRETS__BACKEND_KWARG__SECRET_ID` and `AIRFLOW__WORKERS__SECRETS_BACKEND_KWARG__SECRET_ID`) as synthetic config options whose option names were not in `sensitive_config_values`, so the masker did not redact them. An authenticated UI/API user with Config read permission could retrieve plaintext secrets-backend credentials (Vault `role_id` / `secret_id`, etc.) from the Config API output. Affects deployments that configure secrets backends via per-key environment overrides. Users are advised to upgrade to `apache-airflow` 3.3.0 or later.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/4
- https://github.com/apache/airflow/pull/67622
- https://lists.apache.org/thread/pq5yy40079h6tzh3fxvw28dd8dbk72hk
- https://nvd.nist.gov/vuln/detail/CVE-2026-48892
