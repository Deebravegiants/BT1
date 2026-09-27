# [M] Keyfile contents are in MongoDB Server logs

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-9735
Aliases: CVE-2026-9735
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9735
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
MongoDB server may log authentication parameters, including credentials, to the server log during SASL authentication. When connection health metric logging is enabled, the full authentication parameters are written to the log without redaction.

## References
- https://jira.mongodb.org/browse/SERVER-126506
- https://nvd.nist.gov/vuln/detail/CVE-2026-9735
