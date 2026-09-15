# [H] An unsafe cast in the MongoDB query planner can result in a segmentation fault.

## Summary
Severity: High
Advisory: BIT-mongodb-2026-25613
Aliases: CVE-2026-25613
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-25613
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.4

## Details
An authorized user may disable the MongoDB server by issuing a query against a collection that contains an invalid compound wildcard index.

## References
- https://jira.mongodb.org/browse/SERVER-113685
- https://nvd.nist.gov/vuln/detail/CVE-2026-25613
