# [H] tlsCATrusts Role Restriction Not Enforced via PROXY Protocol v2 on Unix Domain Socket

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13067
Aliases: CVE-2026-13067
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13067
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
When PROXY protocol v2 is used on the Unix domain socket path, roles derived from X.509 client certificates may not be validated against the configured tlsCATrusts allow-list. This can result in unintended role assignments following MONGODB-X509 authentication. Affected scenarios require local access to the proxy Unix domain socket and a valid X.509 certificate issued by a trusted certificate authority.

## References
- https://jira.mongodb.org/browse/SERVER-128387
- https://nvd.nist.gov/vuln/detail/CVE-2026-13067
