# [M] BIT-node-2022-32222

## Summary
Severity: Medium
Advisory: BIT-node-2022-32222
Aliases: BIT-node-min-2022-32222, CVE-2022-32222
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-32222
Type: osv

## Affected
- Bitnami: `node` — affected >=18.0.0 <18.5.0

## Details
A cryptographic vulnerability exists on Node.js on linux in versions of 18.x prior to 18.40.0 which allowed a default path for openssl.cnf that might be accessible under some circumstances to a non-admin user instead of /etc/ssl as was the case in versions prior to the upgrade to OpenSSL 3.

## References
- https://hackerone.com/reports/1695596
- https://nvd.nist.gov/vuln/detail/CVE-2022-32222
