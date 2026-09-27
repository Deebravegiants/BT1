# [M] BIT-node-2022-32215

## Summary
Severity: Medium
Advisory: BIT-node-2022-32215
Aliases: BIT-node-min-2022-32215, CVE-2022-32215
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-32215
Type: osv

## Affected
- Bitnami: `node` — affected >=18.0.0 <18.5.0

## Details
The llhttp parser <v14.20.1, <v16.17.1 and <v18.9.1 in the http module in Node.js does not correctly handle multi-line Transfer-Encoding headers. This can lead to HTTP Request Smuggling (HRS).

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-332410.pdf
- https://hackerone.com/reports/1501679
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ICG6CSIB3GUWH5DUSQEVX53MOJW7LYK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QCNN3YG2BCLS4ZEKJ3CLSUT6AS7AXTH3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VMQK5L5SBYD47QQZ67LEMHNQ662GH3OY/
- https://nodejs.org/en/blog/vulnerability/july-2022-security-releases/
- https://www.debian.org/security/2023/dsa-5326
- https://nvd.nist.gov/vuln/detail/CVE-2022-32215
