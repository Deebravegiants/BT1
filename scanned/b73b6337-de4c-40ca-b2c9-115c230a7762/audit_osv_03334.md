# [H] ALPINE-CVE-2025-55131

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-55131
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-55131
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.13.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.13.0-r0

## Details
A flaw in Node.js's buffer allocation logic can expose uninitialized memory when allocations are interrupted, when using the `vm` module with the timeout option. Under specific timing conditions, buffers allocated with `Buffer.alloc` and other `TypedArray` instances like `Uint8Array` may contain leftover data from previous operations, allowing in-process secrets like tokens or passwords to leak or causing data corruption. While exploitation typically requires precise timing or in-process code execution, it can become remotely exploitable when untrusted input influences workload and timeouts, leading to potential confidentiality and integrity impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-55131
