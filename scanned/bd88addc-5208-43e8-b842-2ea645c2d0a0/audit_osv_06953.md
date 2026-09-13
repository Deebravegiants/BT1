# [H] Server crash via malformed binary diff passed to $_internalApplyOplogUpdate.

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9753
Aliases: CVE-2026-9753
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9753
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
The $_internalApplyOplogUpdate aggregation pipeline stage can be used to execute a document diff containing a malformed binary diff to return memory out-of-bounds or crash the server. $_internalApplyOplogUpdate can be executed by any authenticated user with access to the aggregate command.

## References
- https://jira.mongodb.org/browse/SERVER-124959
- https://nvd.nist.gov/vuln/detail/CVE-2026-9753
