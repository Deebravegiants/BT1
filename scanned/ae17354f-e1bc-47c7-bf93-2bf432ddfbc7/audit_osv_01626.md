# [H] ALPINE-CVE-2019-6477

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6477
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6477
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.11: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.12: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.13: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.14: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.15: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.16: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.17: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.18: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.19: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.20: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.21: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.22: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.23: `bind` — affected >=9.11.7 <9.14.8-r0
- Alpine:v3.24: `bind` — affected >=9.11.7 <9.14.8-r0

## Details
With pipelining enabled each incoming query on a TCP connection requires a similar resource allocation to a query received via UDP or via TCP without pipelining enabled. A client using a TCP-pipelined connection to a server could consume more resources than the server has been provisioned to handle. When a TCP connection with a large number of pipelined queries is closed, the load on the server releasing these multiple resources can cause it to become unresponsive, even for queries that can be answered authoritatively or from cache. (This is most likely to be perceived as an intermittent server problem).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6477
