# [C] BIT-node-2022-35255

## Summary
Severity: Critical
Advisory: BIT-node-2022-35255
Aliases: BIT-node-min-2022-35255, CVE-2022-35255
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-35255
Type: osv

## Affected
- Bitnami: `node` — affected >=18.0.0 <18.9.1

## Details
A weak randomness in WebCrypto keygen vulnerability exists in Node.js 18 due to a change with EntropySource() in SecretKeyGenTraits::DoKeyGen() in src/crypto/crypto_keygen.cc. There are two problems with this: 1) It does not check the return value, it assumes EntropySource() always succeeds, but it can (and sometimes will) fail. 2) The random data returned byEntropySource() may not be cryptographically strong and therefore not suitable as keying material.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-332410.pdf
- https://hackerone.com/reports/1690000
- https://security.netapp.com/advisory/ntap-20230113-0002/
- https://www.debian.org/security/2023/dsa-5326
- https://nvd.nist.gov/vuln/detail/CVE-2022-35255
