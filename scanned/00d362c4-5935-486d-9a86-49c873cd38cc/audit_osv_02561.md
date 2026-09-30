# [H] ALPINE-CVE-2022-31144

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-31144
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-31144
Type: osv

## Affected
- Alpine:v3.16: `redis` — affected >=7.0 <7.0.4-r0
- Alpine:v3.17: `redis` — affected >=7.0 <7.0.4-r0
- Alpine:v3.18: `redis` — affected >=7.0 <7.0.4-r0
- Alpine:v3.19: `redis` — affected >=7.0 <7.0.4-r0

## Details
Redis is an in-memory database that persists on disk. A specially crafted `XAUTOCLAIM` command on a stream key in a specific state may result with heap overflow, and potentially remote code execution. This problem affects versions on the 7.x branch prior to 7.0.4. The patch is released in version 7.0.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-31144
