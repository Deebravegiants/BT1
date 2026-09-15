# [M] Apache Airflow: Rendered template truncation bypasses nested sensitive-key masking

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-42360
Aliases: CVE-2026-42360, GHSA-cg3x-89rc-x9mw, PYSEC-2026-172
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-airflow-2026-42360
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.2.2

## Details
A bug in Apache Airflow's rendered-template field handling caused nested sensitive-key masking (e.g. nested `password` / `token` / `secret` / `api_key` keys inside a JSON template structure) to be bypassed when the rendered field exceeded `[core] max_templated_field_length`: Airflow stringified the structure before redaction, losing the nested key context, and persisted the plaintext value into `rendered_fields`. An authenticated UI/API user with permission to read rendered template fields could harvest secret values intended to be masked. Affects deployments where Dag authors pass structured JSON to operators with nested sensitive keys. This is a variant of `CWE-200` previously addressed for the user-registered `mask_secret()` patterns in CVE-2025-68438; that fix did not cover the nested sensitive-keyword allowlist. Users who already upgraded for CVE-2025-68438 should additionally upgrade to `apache-airflow` 3.2.2 or later to cover the nested-key path.

## References
- https://github.com/apache/airflow/pull/65906
- https://lists.apache.org/thread/obj79bpxnl7r5olz1gsn0g94y88glnl4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42360
