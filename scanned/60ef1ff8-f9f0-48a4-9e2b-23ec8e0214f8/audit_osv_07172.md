# [C] BIT-node-2026-21636

## Summary
Severity: Critical
Advisory: BIT-node-2026-21636
Aliases: BIT-node-min-2026-21636, CVE-2026-21636
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2026-21636
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.3.0

## Details
A flaw in Node.js's permission model allows Unix Domain Socket (UDS) connections to bypass network restrictions when `--permission` is enabled. Even without `--allow-net`, attacker-controlled inputs (such as URLs or socketPath options) can connect to arbitrary local sockets via net, tls, or undici/fetch. This breaks the intended security boundary of the permission model and enables access to privileged local services, potentially leading to privilege escalation, data exposure, or local code execution.

* The issue affects users of the Node.js permission model on version v25.

In the moment of this vulnerability, network permissions (`--allow-net`) are still in the experimental phase.

## References
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21636
