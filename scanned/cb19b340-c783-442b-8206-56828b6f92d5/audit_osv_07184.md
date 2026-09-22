# [M] BIT-node-2026-48928

## Summary
Severity: Medium
Advisory: BIT-node-2026-48928
Aliases: BIT-node-min-2026-48928, CVE-2026-48928
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-node-2026-48928
Type: osv

## Affected
- Bitnami: `node` — affected >=26.3.0 <26.3.1

## Details
A inconsistency in Node.js hostname matching can cause a trust-policy bypass in multi-context mTLS setups.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48928
