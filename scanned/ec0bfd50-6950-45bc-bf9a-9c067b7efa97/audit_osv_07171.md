# [H] BIT-node-2025-59466

## Summary
Severity: High
Advisory: BIT-node-2025-59466
Aliases: BIT-node-min-2025-59466, CVE-2025-59466
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2025-59466
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.3.0

## Details
We have identified a bug in Node.js error handling where "Maximum call stack size exceeded" errors become uncatchable when `async_hooks.createHook()` is enabled. Instead of reaching `process.on('uncaughtException')`, the process terminates, making the crash unrecoverable. Applications that rely on `AsyncLocalStorage` (v22, v20) or `async_hooks.createHook()` (v24, v22, v20) become vulnerable to denial-of-service crashes triggered by deep recursion under specific conditions.

## References
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-59466
