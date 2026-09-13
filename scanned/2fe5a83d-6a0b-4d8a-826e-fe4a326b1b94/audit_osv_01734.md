# [H] ALPINE-CVE-2020-12662

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-12662
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12662
Type: osv

## Affected
- Alpine:v3.10: `unbound` — affected >=0 <1.9.1-r8
- Alpine:v3.11: `unbound` — affected >=0 <1.9.6-r1
- Alpine:v3.12: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.13: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.14: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.15: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.16: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.17: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.10.1-r0
- Alpine:v3.9: `unbound` — affected >=0 <1.8.3-r4

## Details
Unbound before 1.10.1 has Insufficient Control of Network Message Volume, aka an "NXNSAttack" issue. This is triggered by random subdomains in the NSDNAME in NS records.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12662
