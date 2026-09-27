# [H] ALPINE-CVE-2021-32762

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32762
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32762
Type: osv

## Affected
- Alpine:v3.11: `redis` — affected >=5.0.0 <5.0.14-r0
- Alpine:v3.12: `redis` — affected >=5.0.0 <5.0.14-r0
- Alpine:v3.13: `redis` — affected >=5.0.0 <6.0.16-r0
- Alpine:v3.14: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.15: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.16: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.17: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.18: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.19: `redis` — affected >=5.0.0 <6.2.6-r0

## Details
Redis is an open source, in-memory database that persists on disk. The redis-cli command line tool and redis-sentinel service may be vulnerable to integer overflow when parsing specially crafted large multi-bulk network replies. This is a result of a vulnerability in the underlying hiredis library which does not perform an overflow check before calling the calloc() heap allocation function. This issue only impacts systems with heap allocators that do not perform their own overflow checks. Most modern systems do and are therefore not likely to be affected. Furthermore, by default redis-sentinel uses the jemalloc allocator which is also not vulnerable. The problem is fixed in Redis versions 6.2.6, 6.0.16 and 5.0.14.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32762
