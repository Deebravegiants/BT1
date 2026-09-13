# [M] Apache Airflow: Variable masker depth-limit bypass returns cleartext nested secrets

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-42358
Aliases: CVE-2026-42358, GHSA-33g2-gx67-c2h3, PYSEC-2026-2343
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-airflow-2026-42358
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.2.2

## Details
A bug in Apache Airflow's Variable response masker caused nested-key redaction (triggered by secret-suffixed key names like `password`, `token`, `secret`, `api_key`) to be bypassed when the JSON value's nesting depth exceeded the shared secrets masker's recursion limit: the masker returned the original nested item before checking the sensitive key name. An authenticated UI/API user with Variable read permission could harvest plaintext secret values stored under sensitive keys nested deep enough to exceed the masker's depth cap. Affects deployments that store sensitive values inside deeply-nested JSON Variables. This is a residual gap in the fix for CVE-2026-32690 (which covered shallower nesting via `max_depth=1`); the depth-limit boundary itself was not raised, so the same key-name bypass pattern reappears beyond the recursion cap. Users who already upgraded for CVE-2026-32690 should additionally upgrade to `apache-airflow` 3.2.2 or later to cover the deep-nesting path.

## References
- https://github.com/apache/airflow/pull/65912
- https://lists.apache.org/thread/33635mv3zjb75wn5453c5yf9trs8x2om
- https://nvd.nist.gov/vuln/detail/CVE-2026-42358
