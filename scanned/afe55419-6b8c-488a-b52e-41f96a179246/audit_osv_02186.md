# [H] ALPINE-CVE-2021-29477

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-29477
Ecosystem: Alpine:v3.13
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29477
Type: osv

## Affected
- Alpine:v3.13: `redis` — affected >=6.0.0 <6.0.13-r0

## Details
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker. An integer overflow bug in Redis version 6.0 or newer could be exploited using the `STRALGO LCS` command to corrupt the heap and potentially result with remote code execution. The problem is fixed in version 6.2.3 and 6.0.13. An additional workaround to mitigate the problem without patching the redis-server executable is to use ACL configuration to prevent clients from using the `STRALGO LCS` command.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29477
