# [M] Apache Airflow: Bulk Variable and Connection endpoints record secret values in the audit log in cleartext

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-68969
Aliases: CVE-2026-68969, PYSEC-2026-3711
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-68969
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow wrote Variable values and Connection `extra` contents to the audit log in cleartext when they were submitted through the bulk endpoints (`PATCH /api/v2/variables` and `PATCH /api/v2/connections`). The audit-log masking recognised only top-level request fields, and a bulk request nests its entities two levels below, so no masking was applied to them. Any authenticated user with audit-log read access -- who need not hold Variables or Connections read at all -- could recover those secrets verbatim, and the Connection `extra` copy is stored unencrypted in the log while the connection table encrypts it. The Airflow UI's *Import Variables* action posts to this endpoint, so an ordinary operator import wrote every secret in the file to the log. This is a different code path from CVE-2026-50204: that fix shipped in 3.3.0 and covers the single-entity endpoints only, so deployments that upgraded in response to that advisory remain affected and must upgrade again. Users are advised to upgrade to apache-airflow 3.3.1 or later.

## References
- https://github.com/apache/airflow/pull/70890
- https://lists.apache.org/thread/p3jr90jgp2brto4vwcrx680f3x11y70c
- https://nvd.nist.gov/vuln/detail/CVE-2026-68969
- https://www.cve.org/CVERecord?id=CVE-2026-50204
