# [H] BIT-node-2026-56846

## Summary
Severity: High
Advisory: BIT-node-2026-56846
Aliases: BIT-node-min-2026-56846, CVE-2026-56846
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-56846
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <24.18.1

## Details
A flaw in Node.js HTTP/2 handling can cause HTTP/2 retained header blocks evade maxSessionMemory and enable remote memory exhaustion.

This vulnerability affects Node.js **24.x** and **22.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-56846
