# [H] ALPINE-CVE-2026-23631

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-23631
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23631
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.7-r0
- Alpine:v3.23: `valkey` — affected >=0 <9.0.4-r0
- Alpine:v3.24: `valkey` — affected >=0 <9.0.4-r0

## Details
Redis is an in-memory data structure store. In all versions of redis-server with Lua scripting, an authenticated attacker can exploit the master-replica synchronization mechanism to trigger a use-after-free on replicas where replica-read-only is disabled or can be disabled, which may lead to remote code execution. A workaround is to prevent users from executing Lua scripts or avoid using replicas where replica-read-only is disabled. This is patched in version 8.6.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23631
