# [M] BIT-node-2026-56847

## Summary
Severity: Medium
Advisory: BIT-node-2026-56847
Aliases: BIT-node-min-2026-56847, CVE-2026-56847
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-56847
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js Permission Model enforcement allows `trace_events.createTracing().enable()` Writes Trace Logs Outside `--allow-fs-write`.

This can lead to confidentiality impact or bypass of the intended security boundary under affected configurations.

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-56847
