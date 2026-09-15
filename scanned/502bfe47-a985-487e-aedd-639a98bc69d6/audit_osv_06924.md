# [H] Connections received from the proxy port may not count towards total accepted connections

## Summary
Severity: High
Advisory: BIT-mongodb-2026-1848
Aliases: CVE-2026-1848
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-1848
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.4

## Details
Connections received from the proxy port may not count towards total accepted connections, resulting in server crashes if the total number of connections exceeds available resources. This only applies to connections accepted from the proxy port, pending the proxy protocol header.

## References
- https://jira.mongodb.org/browse/SERVER-114695
- https://nvd.nist.gov/vuln/detail/CVE-2026-1848
