# [H] BIT-node-2026-48617

## Summary
Severity: High
Advisory: BIT-node-2026-48617
Aliases: BIT-node-min-2026-48617, CVE-2026-48617
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-node-2026-48617
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.3.1

## Details
A flaw in Node.js Permission Model enforcement allows Bypass via `process.report.writeReport()` Path Misvalidation. This can lead to confidentiality impact or bypass of the intended security boundary under affected configurations. This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- http://hackerone.com/reports/3692858
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48617
