# [H] BIT-node-2026-56848

## Summary
Severity: High
Advisory: BIT-node-2026-56848
Aliases: BIT-node-min-2026-56848, CVE-2026-56848
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-56848
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js HTTP/2 handling allows `nghttp2_session_mem_send()` to be called re-entrantly while `nghttp2_session_mem_recv()` is executing, resulting in a heap-use-after-free.

This vulnerability affects Node.js **26.x**, **24.x**, and **22.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-56848
