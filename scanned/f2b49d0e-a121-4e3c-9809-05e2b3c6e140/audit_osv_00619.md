# [M] ALPINE-CVE-2017-3143

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3143
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3143
Type: osv

## Affected
- Alpine:v3.3: `bind` — affected >=9.4.0 <9.10.4_p8-r1
- Alpine:v3.4: `bind` — affected >=9.4.0 <9.10.4_p8-r1
- Alpine:v3.5: `bind` — affected >=9.4.0 <9.10.4_p8-r1
- Alpine:v3.6: `bind` — affected >=9.4.0 <9.11.1_p1-r1
- Alpine:v3.7: `bind` — affected >=9.4.0 <9.11.3-r0

## Details
An attacker who is able to send and receive messages to an authoritative DNS server and who has knowledge of a valid TSIG key name for the zone and service being targeted may be able to manipulate BIND into accepting an unauthorized dynamic update. Affects BIND 9.4.0->9.8.8, 9.9.0->9.9.10-P1, 9.10.0->9.10.5-P1, 9.11.0->9.11.1-P1, 9.9.3-S1->9.9.10-S2, 9.10.5-S1->9.10.5-S2.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3143
