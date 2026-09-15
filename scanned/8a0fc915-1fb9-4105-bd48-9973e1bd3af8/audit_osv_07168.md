# [M] BIT-node-2025-55132

## Summary
Severity: Medium
Advisory: BIT-node-2025-55132
Aliases: BIT-node-min-2025-55132, CVE-2025-55132
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2025-55132
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.3.0

## Details
A flaw in Node.js's permission model allows a file's access and modification timestamps to be changed via `futimes()` even when the process has only read permissions. Unlike `utimes()`, `futimes()` does not apply the expected write-permission checks, which means file metadata can be modified in read-only directories. This behavior could be used to alter timestamps in ways that obscure activity, reducing the reliability of logs. This vulnerability affects users of the permission model on Node.js v20,  v22,  v24, and v25.

## References
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-55132
