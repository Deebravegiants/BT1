# [M] BIT-node-2026-56850

## Summary
Severity: Medium
Advisory: BIT-node-2026-56850
Aliases: BIT-node-min-2026-56850, CVE-2026-56850
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-56850
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js HTTPS Agent connection reuse can cause PFX object-array key collisions, allowing mutual TLS (mTLS) client identities to be reused across requests configured with different client certificates.

This vulnerability affects Node.js **26.x**, **24.x**, and **22.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-56850
