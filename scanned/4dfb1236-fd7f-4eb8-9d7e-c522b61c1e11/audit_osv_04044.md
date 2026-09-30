# [M] Apache Airflow: Secrets masker: `var.json` Variable values not masked in the Rendered Templates UI

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-59244
Aliases: CVE-2026-59244, PYSEC-2026-3706
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-59244
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's secrets masker did not mask `var.json` Variable values whose value is a dict in the Rendered Templates UI — the dict value failed an `isinstance(str)` guard — so a secret stored as a JSON Variable and referenced in a template via `var.json` was displayed in cleartext to any user with access to that task's Rendered Templates view. Users are advised to upgrade to apache-airflow 3.3.1 or later, which masks nested Variable values regardless of type.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/7
- https://github.com/apache/airflow/pull/68975
- https://lists.apache.org/thread/fncod6vttfo5fvmfs3h9r8s2kmm9j1n6
- https://nvd.nist.gov/vuln/detail/CVE-2026-59244
