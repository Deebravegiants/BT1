# [M] ALPINE-CVE-2017-3135

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3135
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3135
Type: osv

## Affected
- Alpine:v3.2: `bind` — affected >=0 <9.10.4_p6-r0
- Alpine:v3.3: `bind` — affected >=0 <9.10.4_p6-r0
- Alpine:v3.4: `bind` — affected >=0 <9.10.4_p6-r0
- Alpine:v3.5: `bind` — affected >=0 <9.10.4_p6-r0

## Details
Under some conditions when using both DNS64 and RPZ to rewrite query responses, query processing can resume in an inconsistent state leading to either an INSIST assertion failure or an attempt to read through a NULL pointer. Affects BIND 9.8.8, 9.9.3-S1 -> 9.9.9-S7, 9.9.3 -> 9.9.9-P5, 9.9.10b1, 9.10.0 -> 9.10.4-P5, 9.10.5b1, 9.11.0 -> 9.11.0-P2, 9.11.1b1.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3135
