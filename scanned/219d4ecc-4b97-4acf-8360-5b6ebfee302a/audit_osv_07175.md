# [M] BIT-node-2026-21711

## Summary
Severity: Medium
Advisory: BIT-node-2026-21711
Aliases: BIT-node-min-2026-21711, CVE-2026-21711
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-node-2026-21711
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.8.2

## Details
A flaw in Node.js Permission Model network enforcement leaves Unix Domain Socket (UDS) server operations without the required permission checks, while all comparable network paths correctly enforce them.

As a result, code running under `--permission` without `--allow-net` can create and expose local IPC endpoints, allowing communication with other processes on the same host outside of the intended network restriction boundary.

This vulnerability affects Node.js **25.x** processes using the Permission Model where `--allow-net` is intentionally omitted to restrict network access. Note that `--allow-net` is currently an experimental feature.

## References
- https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21711
