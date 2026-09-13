# [H] ALPINE-CVE-2023-41056

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-41056
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-41056
Type: osv

## Affected
- Alpine:v3.16: `redis` — affected >=7.0.9 <7.0.15-r0
- Alpine:v3.17: `redis` — affected >=7.0.9 <7.0.15-r0
- Alpine:v3.18: `redis` — affected >=7.0.9 <7.0.15-r0
- Alpine:v3.19: `redis` — affected >=7.0.9 <7.2.4-r0

## Details
Redis is an in-memory database that persists on disk. Redis incorrectly handles resizing of memory buffers which can result in integer overflow that leads to heap overflow and potential remote code execution. This issue has been patched in version 7.0.15 and 7.2.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-41056
