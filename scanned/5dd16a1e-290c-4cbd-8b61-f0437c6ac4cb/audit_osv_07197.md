# [M] BIT-node-2026-58045

## Summary
Severity: Medium
Advisory: BIT-node-2026-58045
Aliases: BIT-node-min-2026-58045, CVE-2026-58045
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-58045
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js allows a spoofed `TypedArray` `byteLength` to trigger a reachable assertion in the synchronous `node:zlib` APIs, causing the entire process to crash. All 11 synchronous zlib functions are affected.

Repeated exploitation of this condition can result in a denial of service.

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-58045
