# [H] ALPINE-CVE-2021-32625

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32625
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32625
Type: osv

## Affected
- Alpine:v3.13: `redis` — affected >=6.0.0 <6.0.14-r0
- Alpine:v3.14: `redis` — affected >=6.0.0 <6.2.4-r0
- Alpine:v3.15: `redis` — affected >=6.0.0 <6.2.4-r0
- Alpine:v3.16: `redis` — affected >=6.0.0 <6.2.4-r0
- Alpine:v3.17: `redis` — affected >=6.0.0 <6.2.4-r0
- Alpine:v3.18: `redis` — affected >=6.0.0 <6.2.4-r0
- Alpine:v3.19: `redis` — affected >=6.0.0 <6.2.4-r0

## Details
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker. An integer overflow bug in Redis version 6.0 or newer, could be exploited using the STRALGO LCS command to corrupt the heap and potentially result with remote code execution. This is a result of an incomplete fix by CVE-2021-29477. The problem is fixed in version 6.2.4 and 6.0.14. An additional workaround to mitigate the problem without patching the redis-server executable is to use ACL configuration to prevent clients from using the STRALGO LCS command. On 64 bit systems which have the fixes of CVE-2021-29477 (6.2.3 or 6.0.13), it is sufficient to make sure that the proto-max-bulk-len config parameter is smaller than 2GB (default is 512MB).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32625
