# [H] ALPINE-CVE-2026-23479

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-23479
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23479
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.7-r0
- Alpine:v3.23: `valkey` — affected >=0 <9.0.4-r0
- Alpine:v3.24: `valkey` — affected >=0 <9.0.4-r0

## Details
Redis is an in-memory data structure store. In redis-server from 7.2.0 until 8.6.3, the unblock client flow does not handle an error return from `processCommandAndResetClient` when re-executing a blocked command. If a blocked client is evicted during this flow, an authenticated attacker can trigger a use-after-free that may lead to remote code execution. This has been patched in version 8.6.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23479
