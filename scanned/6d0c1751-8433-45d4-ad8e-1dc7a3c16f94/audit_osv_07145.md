# [H] BIT-node-2023-39331

## Summary
Severity: High
Advisory: BIT-node-2023-39331
Aliases: BIT-node-min-2023-39331, CVE-2023-39331
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-39331
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.8.1

## Details
A previously disclosed vulnerability (CVE-2023-30584) was patched insufficiently in commit 205f1e6. The new path traversal vulnerability arises because the implementation does not protect itself against the application overwriting built-in utility functions with user-defined implementations.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2092852
- https://security.netapp.com/advisory/ntap-20231116-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39331
- https://security.netapp.com/advisory/ntap-20241108-0002/
