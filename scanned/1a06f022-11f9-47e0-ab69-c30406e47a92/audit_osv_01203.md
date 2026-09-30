# [H] ALPINE-CVE-2018-5738

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5738
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5738
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.11: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.12: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.13: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.14: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.15: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.16: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.17: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.18: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.19: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.20: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.21: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.22: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.23: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.24: `bind` — affected >=0 <9.12.2_p1-r0
- Alpine:v3.6: `bind` — affected >=0 <9.11.5_p4-r0
- Alpine:v3.7: `bind` — affected >=0 <9.11.5_p4-r0
- Alpine:v3.9: `bind` — affected >=0 <9.12.2_p1-r0

## Details
Change #4777 (introduced in October 2017) introduced an unforeseen issue in releases which were issued after that date, affecting which clients are permitted to make recursive queries to a BIND nameserver. The intended (and documented) behavior is that if an operator has not specified a value for the "allow-recursion" setting, it SHOULD default to one of the following: none, if "recursion no;" is set in named.conf; a value inherited from the "allow-query-cache" or "allow-query" settings IF "recursion yes;" (the default for that setting) AND match lists are explicitly set for "allow-query-cache" or "allow-query" (see the BIND9 Administrative Reference Manual section 6.2 for more details); or the intended default of "allow-recursion {localhost; localnets;};" if "recursion yes;" is in effect and no values are explicitly set for "allow-query-cache" or "allow-query". However, because of the regression introduced by change #4777, it is possible when "recursion yes;" is in effect and no match list values are provided for "allow-query-cache" or "allow-query" for the setting of "allow-recursion" to inherit a setting of all hosts from the "allow-query" setting default, improperly permitting recursion to all clients. Affects BIND 9.9.12, 9.10.7, 9.11.3, 9.12.0->9.12.1-P2, the development release 9.13.0, and also releases 9.9.12-S1, 9.10.7-S1, 9.11.3-S1, and 9.11.3-S2 from BIND 9 Supported Preview Edition.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5738
