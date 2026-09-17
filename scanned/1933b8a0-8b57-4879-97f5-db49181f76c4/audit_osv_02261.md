# [M] ALPINE-CVE-2021-3672

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3672
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3672
Type: osv

## Affected
- Alpine:v3.11: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.12: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.13: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.14: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.15: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.16: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.17: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.18: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.19: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.20: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.21: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.22: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.23: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.24: `c-ares` — affected >=1.0.0 <1.17.2-r0
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.5-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.5-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.17.5-r0

## Details
A flaw was found in c-ares library, where a missing input validation check of host names returned by DNS (Domain Name Servers) can lead to output of wrong hostnames which might potentially lead to Domain Hijacking. The highest threat from this vulnerability is to confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3672
