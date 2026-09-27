# [M] ALPINE-CVE-2022-30699

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-30699
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30699
Type: osv

## Affected
- Alpine:v3.17: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.16.2-r0

## Details
NLnet Labs Unbound, up to and including version 1.16.1, is vulnerable to a novel type of the "ghost domain names" attack. The vulnerability works by targeting an Unbound instance. Unbound is queried for a rogue domain name when the cached delegation information is about to expire. The rogue nameserver delays the response so that the cached delegation information is expired. Upon receiving the delayed answer containing the delegation information, Unbound overwrites the now expired entries. This action can be repeated when the delegation information is about to expire making the rogue delegation information ever-updating. From version 1.16.2 on, Unbound stores the start time for a query and uses that to decide if the cached delegation information can be overwritten.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30699
