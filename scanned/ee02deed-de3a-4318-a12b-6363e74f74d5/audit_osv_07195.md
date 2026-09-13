# [M] BIT-node-2026-58042

## Summary
Severity: Medium
Advisory: BIT-node-2026-58042
Aliases: BIT-node-min-2026-58042, CVE-2026-58042
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-58042
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js can cause dns.resolveAny() Aborts the Node.js Process When a DNS Response Contains More Than 256 A Records.

Repeated triggering of this condition can lead to denial of service.

This vulnerability affects Node.js **26.x**, **24.x**, and **22.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-58042
