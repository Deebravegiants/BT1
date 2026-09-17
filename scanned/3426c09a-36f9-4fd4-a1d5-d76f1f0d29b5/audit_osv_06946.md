# [H] Aggregation sub-pipeline null dereference may allow DoS via crafted getMore

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9743
Aliases: CVE-2026-9743
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9743
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.24

## Details
In MongoDB Server 8.0, an aggregation stage can leave its _subPipeline field null during processing of certain pipelines. If a getMore is subsequently issued on the same cursor, the server may dereference this null sub-pipeline when reattaching to the operation context, accessing an invalid address and crashing the process. This issue allows an authenticated user who can run aggregation pipelines to cause a denial of service by issuing a specially crafted aggregation followed by getMore on affected versions.

## References
- https://jira.mongodb.org/browse/SERVER-123688
- https://nvd.nist.gov/vuln/detail/CVE-2026-9743
