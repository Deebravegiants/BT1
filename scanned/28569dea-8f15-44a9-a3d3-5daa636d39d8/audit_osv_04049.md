# [M] Apache Airflow: Values of a list-shaped Variable are not masked in task logs and the Rendered Templates UI

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-68970
Aliases: CVE-2026-68970, PYSEC-2026-3712
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-68970
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's Task SDK did not mask the contents of a Variable whose JSON value is a list, so secrets stored in that shape appeared in cleartext in task logs and in the Rendered Templates UI. Masking was applied only when the deserialized value was a string or a dict; a list at the top level matched neither and was returned unmasked. Any authenticated user able to read the logs or rendered templates of a task that references such a Variable could recover the values, with no special configuration required. This is the list-shaped counterpart of CVE-2026-59244, whose fix covered the dict case only, so deployments that upgraded in response to that advisory remain affected and must upgrade again. Users are advised to upgrade to apache-airflow 3.3.1 or later.

## References
- https://github.com/apache/airflow/pull/70891
- https://lists.apache.org/thread/kkrlnbsk47oght4h38mcd3h2kcb8dt28
- https://nvd.nist.gov/vuln/detail/CVE-2026-68970
- https://www.cve.org/CVERecord?id=CVE-2026-59244
