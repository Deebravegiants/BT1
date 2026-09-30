# [C] MongoDB Server running on Linux may allow unexpected connections where intermediate certificates are revoked

## Summary
Severity: Critical
Advisory: BIT-mongodb-2025-3085
Aliases: CVE-2025-3085
Ecosystem: Bitnami
Published: 2025-09-25
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-3085
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.4

## Details
A MongoDB server under specific conditions running on Linux with TLS and CRL revocation status checking enabled, fails to check the revocation status of the intermediate certificates in the peer's certificate chain. In cases of MONGODB-X509, which is not enabled by default, this may lead to improper authentication. This issue may also affect intra-cluster authentication. This issue affects MongoDB Server v5.0 versions prior to 5.0.31, MongoDB Server v6.0 versions prior to 6.0.20, MongoDB Server v7.0 versions prior to 7.0.16 and MongoDB Server v8.0 versions prior to 8.0.4.
Required Configuration : MongoDB Server must be running on Linux Operating Systems and CRL revocation status checking must be enabled

## References
- https://jira.mongodb.org/browse/SERVER-95445
- https://nvd.nist.gov/vuln/detail/CVE-2025-3085
