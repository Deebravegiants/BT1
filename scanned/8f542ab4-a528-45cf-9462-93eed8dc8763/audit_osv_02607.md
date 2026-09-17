# [C] ALPINE-CVE-2022-35951

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-35951
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35951
Type: osv

## Affected
- Alpine:v3.16: `redis` — affected >=7.0.0 <7.0.5-r0
- Alpine:v3.17: `redis` — affected >=7.0.0 <7.0.5-r0
- Alpine:v3.18: `redis` — affected >=7.0.0 <7.0.5-r0
- Alpine:v3.19: `redis` — affected >=7.0.0 <7.0.5-r0

## Details
Redis is an in-memory database that persists on disk. Versions 7.0.0 and above, prior to 7.0.5 are vulnerable to an Integer Overflow. Executing an `XAUTOCLAIM` command on a stream key in a specific state, with a specially crafted `COUNT` argument may cause an integer overflow, a subsequent heap overflow, and potentially lead to remote code execution. This has been patched in Redis version 7.0.5. No known workarounds exist.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35951
