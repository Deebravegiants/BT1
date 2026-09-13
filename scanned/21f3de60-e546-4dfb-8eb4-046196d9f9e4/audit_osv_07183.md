# [H] BIT-node-2026-48619

## Summary
Severity: High
Advisory: BIT-node-2026-48619
Aliases: BIT-node-min-2026-48619, CVE-2026-48619
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-node-2026-48619
Type: osv

## Affected
- Bitnami: `node` — affected >=26.3.0 <26.3.1

## Details
A flaw in Node.js HTTP/2 client allows a server to send an unlimited number of ORIGIN frames, which could lead to an Out of Memory error on the client.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48619
