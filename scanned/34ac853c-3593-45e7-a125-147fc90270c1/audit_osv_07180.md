# [H] BIT-node-2026-48615

## Summary
Severity: High
Advisory: BIT-node-2026-48615
Aliases: BIT-node-min-2026-48615, CVE-2026-48615
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-node-2026-48615
Type: osv

## Affected
- Bitnami: `node` — affected >=26.3.0 <26.3.1

## Details
A flaw in Node.js proxy tunnel error handling could expose proxy credentials in `ERR_PROXY_TUNNEL` error messages.

When proxy credentials are embedded in the proxy URL, they may be exposed through error handling paths and captured by logs, diagnostics, or other error consumers.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48615
