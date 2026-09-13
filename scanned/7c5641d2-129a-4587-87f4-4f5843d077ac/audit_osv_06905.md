# [H] $graphLookup Aggregation Stage Authorization Check Inconsistency Allowing Unauthorized Collection Access

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13060
Aliases: CVE-2026-13060
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13060
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with limited read privileges may be able to access documents from collections they are not authorized to read, due to an inconsistency in how the $graphLookup aggregation stage is evaluated during authorization and during execution. Affected scenarios involve collections referenced within existing view pipeline definitions.

## References
- https://jira.mongodb.org/browse/SERVER-127357
- https://nvd.nist.gov/vuln/detail/CVE-2026-13060
