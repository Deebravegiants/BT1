# [M] BIT-node-2022-35256

## Summary
Severity: Medium
Advisory: BIT-node-2022-35256
Aliases: BIT-node-min-2022-35256, CVE-2022-35256
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-35256
Type: osv

## Affected
- Bitnami: `node` — affected >=18.0.0 <18.9.1

## Details
The llhttp parser in the http module in Node v18.7.0 does not correctly handle header fields that are not terminated with CLRF. This may result in HTTP Request Smuggling.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-332410.pdf
- https://hackerone.com/reports/1675191
- https://www.debian.org/security/2023/dsa-5326
- https://nvd.nist.gov/vuln/detail/CVE-2022-35256
