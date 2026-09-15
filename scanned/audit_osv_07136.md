# [M] BIT-node-2023-30588

## Summary
Severity: Medium
Advisory: BIT-node-2023-30588
Aliases: BIT-node-min-2023-30588, CVE-2023-30588
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-30588
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.3.1

## Details
When an invalid public key is used to create an x509 certificate using the crypto.X509Certificate() API a non-expect termination occurs making it susceptible to DoS attacks when the attacker could force interruptions of application processing, as the process terminates when accessing public key info of provided certificates from user code. The current context of the users will be gone, and that will cause a DoS scenario. This vulnerability affects all active Node.js versions v16, v18, and, v20.

## References
- https://nodejs.org/en/blog/vulnerability/june-2023-security-releases
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2023-30588
- https://security.netapp.com/advisory/ntap-20241101-0011/
