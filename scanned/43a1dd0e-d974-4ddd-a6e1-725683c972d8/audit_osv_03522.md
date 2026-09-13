# [H] ALPINE-CVE-2026-25243

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-25243
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-25243
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.13-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.7-r0
- Alpine:v3.23: `valkey` — affected >=0 <9.0.4-r0
- Alpine:v3.24: `valkey` — affected >=0 <9.0.4-r0

## Details
Redis is an in-memory data structure store. In versions of redis-server up to 8.6.3, the RESTORE command does not properly validate serialized values. An authenticated attacker with permission to execute RESTORE can supply a crafted serialized payload that triggers invalid memory access and may lead to remote code execution. A workaround is to restrict access to the RESTORE command with ACL rules. This is patched in version 8.6.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-25243
