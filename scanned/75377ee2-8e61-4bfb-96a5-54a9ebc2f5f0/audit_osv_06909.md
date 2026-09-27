# [H] MongoDB $jsonSchema Query Operator Excessive CPU Consumption Leading to Denial of Service

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13064
Aliases: CVE-2026-13064
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13064
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
Certain query operations involving deeply nested $jsonSchema constructs can trigger disproportionate CPU consumption in affected MongoDB deployments, potentially leading to resource exhaustion. The resulting CPU-bound operation cannot be interrupted through standard administrative controls.

## References
- https://jira.mongodb.org/browse/SERVER-125872
- https://nvd.nist.gov/vuln/detail/CVE-2026-13064
