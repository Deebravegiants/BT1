# [H] BIT-node-2026-58043

## Summary
Severity: High
Advisory: BIT-node-2026-58043
Aliases: BIT-node-min-2026-58043, CVE-2026-58043
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-58043
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js Permission Model enforcement can over-grant filesystem access across radix-tree prefix boundaries.

Under `--permission`, an attacker who is granted access to one path can abuse boundary handling to read from or write to paths outside the intended filesystem allowlist.

This vulnerability affects Node.js **main**, **22.x**, **24.x**, and **26.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-58043
