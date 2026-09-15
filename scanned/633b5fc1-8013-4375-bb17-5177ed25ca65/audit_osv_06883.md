# [H] MongoDB may be susceptible to Invariant Failure due to batched delete

## Summary
Severity: High
Advisory: BIT-mongodb-2025-13644
Aliases: CVE-2025-13644
Ecosystem: Bitnami
Published: 2025-12-12
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-13644
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.1.0 <8.1.2

## Details
MongoDB Server may experience an invariant failure during batched delete operations when handling documents. The issue arises when the server mistakenly assumes the presence of multiple documents in a batch based solely on document size exceeding BSONObjMaxSize. This issue affects MongoDB Server v7.0 versions prior to 7.0.26, MongoDB Server v8.0 versions prior to 8.0.13, and MongoDB Server v8.1 versions prior to 8.1.2

## References
- https://jira.mongodb.org/browse/SERVER-101180
- https://nvd.nist.gov/vuln/detail/CVE-2025-13644
