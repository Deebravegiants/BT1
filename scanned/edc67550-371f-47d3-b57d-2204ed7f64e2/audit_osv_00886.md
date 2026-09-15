# [M] ALPINE-CVE-2018-1052

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1052
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1052
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.11: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.12: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.13: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.14: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.7: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.8: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.9: `postgresql` — affected >=0 <10.2-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.2-r0

## Details
Memory disclosure vulnerability in table partitioning was found in postgresql 10.x before 10.2, allowing an authenticated attacker to read arbitrary bytes of server memory via purpose-crafted insert to a partitioned table.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1052
