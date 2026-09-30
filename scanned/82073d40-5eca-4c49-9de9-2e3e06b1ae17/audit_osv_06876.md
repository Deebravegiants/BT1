# [H] MongoDB may be susceptible to Invariant Failure in Transactions due Upsert Operation

## Summary
Severity: High
Advisory: BIT-mongodb-2025-10060
Aliases: CVE-2025-10060
Ecosystem: Bitnami
Published: 2025-09-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-10060
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.12

## Details
MongoDB Server may allow upsert operations retried within a transaction to violate unique index constraints, potentially causing an invariant failure and server crash during commit. This issue may be triggered by improper WriteUnitOfWork state management.  This issue affects MongoDB Server v6.0 versions prior to 6.0.25, MongoDB Server v7.0 versions prior to 7.0.22 and MongoDB Server v8.0 versions prior to 8.0.12

## References
- https://jira.mongodb.org/browse/SERVER-95524
- https://nvd.nist.gov/vuln/detail/CVE-2025-10060
