# [M] BIT-node-2026-21713

## Summary
Severity: Medium
Advisory: BIT-node-2026-21713
Aliases: BIT-node-min-2026-21713, CVE-2026-21713
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-node-2026-21713
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.8.2

## Details
A flaw in Node.js HMAC verification uses a non-constant-time comparison when validating user-provided signatures, potentially leaking timing information proportional to the number of matching bytes. Under certain threat models where high-resolution timing measurements are possible, this behavior could be exploited as a timing oracle to infer HMAC values.

Node.js already provides timing-safe comparison primitives used elsewhere in the codebase, indicating this is an oversight rather than an intentional design decision.

This vulnerability affects **20.x, 22.x, 24.x, and 25.x**.

## References
- https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21713
