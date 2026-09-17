# [H] Certificate validation issue in MongoDB Server running on Windows or macOS

## Summary
Severity: High
Advisory: BIT-mongodb-2023-1409
Aliases: CVE-2023-1409
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2023-1409
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=6.3.0 <6.3.3

## Details
If the MongoDB Server running on Windows or macOS is configured to use TLS with a specific set of configuration options that are already known to work securely in other platforms (e.g. Linux), it is possible that client certificate validation may not be in effect, potentially allowing client to establish a TLS connection with the server that supplies any certificate.

This issue affect all MongoDB Server v6.3 versions, MongoDB Server v5.0 versions v5.0.0 to v5.0.14 and all MongoDB Server v4.4 versions.

## References
- https://jira.mongodb.org/browse/SERVER-73662
- https://jira.mongodb.org/browse/SERVER-77028
- https://security.netapp.com/advisory/ntap-20230921-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1409
