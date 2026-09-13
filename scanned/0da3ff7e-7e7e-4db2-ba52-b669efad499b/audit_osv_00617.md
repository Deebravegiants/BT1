# [M] ALPINE-CVE-2017-3140

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3140
Ecosystem: Alpine:v3.6, Alpine:v3.7
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3140
Type: osv

## Affected
- Alpine:v3.6: `bind` — affected >=9.11.0 <9.11.3-r0
- Alpine:v3.7: `bind` — affected >=9.11.0 <9.11.3-r0

## Details
If named is configured to use Response Policy Zones (RPZ) an error processing some rule types can lead to a condition where BIND will endlessly loop while handling a query. Affects BIND 9.9.10, 9.10.5, 9.11.0->9.11.1, 9.9.10-S1, 9.10.5-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3140
