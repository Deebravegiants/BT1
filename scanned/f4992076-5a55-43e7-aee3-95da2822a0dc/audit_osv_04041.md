# [M] Apache Airflow: Airflow Variables were not masked in the UI for authenticated users

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-54183
Aliases: CVE-2026-54183, PYSEC-2026-3705
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-54183
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's secrets masker hides values stored under sensitive key names when they are displayed in the UI. The masker's recursion-depth limit did not descend into values nested inside a list, tuple, or set beyond that limit, so an Airflow Variable holding such a deeply-nested value was shown unmasked in the Variables UI. The exposure is limited to the UI: any authenticated user who can see the Variable in the UI can already read its full value through the Variables REST API, so this does not disclose data the user could not otherwise obtain — the masking is a shoulder-surfing defense for the UI, not an access-control boundary.

This is an incomplete-fix follow-up to CVE-2026-42358, whose fix made only the dictionary walk unbounded; lists, tuples, and sets beyond the depth limit remained unmasked in the UI. Deployments that applied the CVE-2026-42358 fix should also upgrade to address this residual case. Upgrade to apache-airflow 3.3.1 or later.

## References
- https://github.com/apache/airflow/pull/68422
- https://lists.apache.org/thread/z5mrdq6c60f2wyx4cc64cj8nv0dxd9lo
- https://nvd.nist.gov/vuln/detail/CVE-2026-54183
- https://www.cve.org/CVERecord?id=CVE-2026-42358
