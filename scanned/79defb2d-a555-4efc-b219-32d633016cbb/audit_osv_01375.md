# [M] ALPINE-CVE-2019-12521

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12521
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12521
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.11: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.9: `squid` — affected >=3.0 <4.11-r0

## Details
An issue was discovered in Squid through 4.7. When Squid is parsing ESI, it keeps the ESI elements in ESIContext. ESIContext contains a buffer for holding a stack of ESIElements. When a new ESIElement is parsed, it is added via addStackElement. addStackElement has a check for the number of elements in this buffer, but it's off by 1, leading to a Heap Overflow of 1 element. The overflow is within the same structure so it can't affect adjacent memory blocks, and thus just leads to a crash while processing.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12521
