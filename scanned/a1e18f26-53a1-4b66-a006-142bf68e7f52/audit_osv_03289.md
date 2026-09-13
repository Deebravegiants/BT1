# [H] ALPINE-CVE-2025-46688

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-46688
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46688
Type: osv

## Affected
- Alpine:v3.23: `quickjs-ng` — affected >=0 <0.10.0-r0
- Alpine:v3.24: `quickjs-ng` — affected >=0 <0.10.0-r0

## Details
quickjs-ng through 0.9.0 has an incorrect size calculation in JS_ReadBigInt for a BigInt, leading to a heap-based buffer overflow. QuickJS before 2025-04-26 is also affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46688
