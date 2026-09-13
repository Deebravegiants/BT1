# [H] Post-auth null pointer dereference when aggregating against a view with empty search pipeline

## Summary
Severity: High
Advisory: BIT-mongodb-2026-8063
Aliases: CVE-2026-8063
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8063
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.7

## Details
An authenticated user can crash mongod when running $rankFusion or $scoreFusion with an empty pipeline on a view.

When resolving a view, the server inspects the aggregation pipeline to determine whether it begins with an Atlas Search stage. For $rankFusion and $scoreFusion, this inspection reads the first element on each stage’s input pipeline array without first verifying that the array is non-empty. Supplying an empty pipeline causes a null pointer dereference and crashes the server.

This issue affects MongoDB Server 8.2 versions prior to 8.2.7.

## References
- https://jira.mongodb.org/browse/SERVER-121851
- https://nvd.nist.gov/vuln/detail/CVE-2026-8063
