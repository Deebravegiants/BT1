# [C] BIT-node-2026-48930

## Summary
Severity: Critical
Advisory: BIT-node-2026-48930
Aliases: BIT-node-min-2026-48930, CVE-2026-48930
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-node-2026-48930
Type: osv

## Affected
- Bitnami: `node` — affected >=26.3.0 <26.3.1

## Details
A flaw in Node.js TLS hostname handling can cause Embedded-nul hostnames can lead to silent authority rebinding due to c-string truncation in resolver bindings.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48930
