# [M] ALPINE-CVE-2023-22458

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-22458
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-22458
Type: osv

## Affected
- Alpine:v3.14: `redis` — affected >=6.2.0 <6.2.9-r0
- Alpine:v3.15: `redis` — affected >=6.2.0 <6.2.9-r0
- Alpine:v3.16: `redis` — affected >=6.2.0 <7.0.8-r0
- Alpine:v3.17: `redis` — affected >=6.2.0 <7.0.8-r0
- Alpine:v3.18: `redis` — affected >=6.2.0 <7.0.8-r0
- Alpine:v3.19: `redis` — affected >=6.2.0 <7.0.8-r0

## Details
Redis is an in-memory database that persists on disk. Authenticated users can issue a `HRANDFIELD` or `ZRANDMEMBER` command with specially crafted arguments to trigger a denial-of-service by crashing Redis with an assertion failure. This problem affects Redis versions 6.2 or newer up to but not including 6.2.9 as well as versions 7.0 up to but not including 7.0.8. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-22458
