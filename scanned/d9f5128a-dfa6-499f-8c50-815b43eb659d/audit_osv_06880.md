# [M] Improper Certificate Validation May Allow Successful TLS Handshaking Despite Invalid Extended Key Usage Fields in MongoDB Server

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-12893
Aliases: CVE-2025-12893
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-12893
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.2

## Details
Clients may successfully perform a TLS handshake with a MongoDB server despite presenting a client certificate not aligning with the documented Extended Key Usage (EKU) requirements. A certificate that specifies extendedKeyUsage but is missing extendedKeyUsage = clientAuth may still be successfully authenticated via the TLS handshake as a client. This issue is specific to MongoDB servers running on Windows or Apple as the expected validation behavior functions correctly on Linux systems.

Additionally, MongoDB servers may successfully establish egress TLS connections with servers that present server certificates not aligning with the documented Extended Key Usage (EKU) requirements. A certificate that specifies extendedKeyUsage but is missing extendedKeyUsage = serverAuth may still be successfully authenticated via the TLS handshake as a server. This issue is specific to MongoDB servers running on Apple as the expected validation behavior functions correctly on both Linux and Windows systems. 

This vulnerability affects MongoDB Server v7.0 versions prior to 7.0.26, MongoDB Server v8.0 versions prior to 8.0.16 and MongoDB Server v8.2 versions prior to 8.2.2

## References
- https://jira.mongodb.org/browse/SERVER-105783
- https://nvd.nist.gov/vuln/detail/CVE-2025-12893
