# [M] BIT-node-2023-23920

## Summary
Severity: Medium
Advisory: BIT-node-2023-23920
Aliases: BIT-node-min-2023-23920, CVE-2023-23920
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-23920
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <19.6.1

## Details
An untrusted search path vulnerability exists in Node.js. <19.6.1, <18.14.1, <16.19.1, and <14.21.3 that could allow an attacker to search and potentially load ICU data when running with elevated privileges.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00038.html
- https://nodejs.org/en/blog/vulnerability/february-2023-security-releases/
- https://security.netapp.com/advisory/ntap-20230316-0008/
- https://www.debian.org/security/2023/dsa-5395
- https://nvd.nist.gov/vuln/detail/CVE-2023-23920
