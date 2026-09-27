# [H] BIT-node-2026-48937

## Summary
Severity: High
Advisory: BIT-node-2026-48937
Aliases: BIT-node-min-2026-48937, CVE-2026-48937
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-node-2026-48937
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <24.17.0

## Details
A flaw in Node.js HTTP/2 server API can cause servers to keep accepting data even after sending a `GOAWAY` frame. This vulnerability affects two supported release lines: **Node.js 22** and **Node.js 24**.

## References
- https://hackerone.com/reports/3658225
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48937
