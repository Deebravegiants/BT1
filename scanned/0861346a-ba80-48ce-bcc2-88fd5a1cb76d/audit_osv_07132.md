# [H] BIT-node-2023-23919

## Summary
Severity: High
Advisory: BIT-node-2023-23919
Aliases: BIT-node-min-2023-23919, CVE-2023-23919
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-23919
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <19.2.0

## Details
A cryptographic vulnerability exists in Node.js <19.2.0, <18.14.1, <16.19.1, <14.21.3 that in some cases did does not clear the OpenSSL error stack after operations that may set it. This may lead to false positive errors during subsequent cryptographic operations that happen to be on the same thread. This in turn could be used to cause a denial of service.

## References
- https://hackerone.com/reports/1808596
- https://nodejs.org/en/blog/vulnerability/february-2023-security-releases/
- https://security.netapp.com/advisory/ntap-20230316-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2023-23919
