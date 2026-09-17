# [H] ALPINE-CVE-2019-10192

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10192
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10192
Type: osv

## Affected
- Alpine:v3.10: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.11: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.12: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.13: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.14: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.15: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.16: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.17: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.18: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.19: `redis` — affected >=3.0.0 <5.0.4-r0
- Alpine:v3.7: `redis` — affected >=3.0.0 <4.0.14-r0
- Alpine:v3.8: `redis` — affected >=3.0.0 <4.0.14-r0
- Alpine:v3.9: `redis` — affected >=3.0.0 <4.0.14-r0

## Details
A heap-buffer overflow vulnerability was found in the Redis hyperloglog data structure versions 3.x before 3.2.13, 4.x before 4.0.14 and 5.x before 5.0.4. By carefully corrupting a hyperloglog using the SETRANGE command, an attacker could trick Redis interpretation of dense HLL encoding to write up to 3 bytes beyond the end of a heap-allocated buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10192
