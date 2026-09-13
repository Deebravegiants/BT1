# [H] ALPINE-CVE-2023-36824

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-36824
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-36824
Type: osv

## Affected
- Alpine:v3.16: `redis` — affected >=7.0.0 <7.0.12-r0
- Alpine:v3.17: `redis` — affected >=7.0.0 <7.0.12-r0
- Alpine:v3.18: `redis` — affected >=7.0.0 <7.0.12-r0
- Alpine:v3.19: `redis` — affected >=7.0.0 <7.0.12-r0

## Details
Redis is an in-memory database that persists on disk. In Redit 7.0 prior to 7.0.12, extracting key names from a command and a list of arguments may, in some cases, trigger a heap overflow and result in reading random heap memory, heap corruption and potentially remote code execution. Several scenarios that may lead to authenticated users executing a specially crafted `COMMAND GETKEYS` or `COMMAND GETKEYSANDFLAGS`and authenticated users who were set with ACL rules that match key names, executing a specially crafted command that refers to a variadic list of key names. The vulnerability is patched in Redis 7.0.12.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-36824
