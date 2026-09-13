# [M] ALPINE-CVE-2026-21713

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-21713
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21713
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A flaw in Node.js HMAC verification uses a non-constant-time comparison when validating user-provided signatures, potentially leaking timing information proportional to the number of matching bytes. Under certain threat models where high-resolution timing measurements are possible, this behavior could be exploited as a timing oracle to infer HMAC values.

Node.js already provides timing-safe comparison primitives used elsewhere in the codebase, indicating this is an oversight rather than an intentional design decision.

This vulnerability affects **20.x, 22.x, 24.x, and 25.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21713
