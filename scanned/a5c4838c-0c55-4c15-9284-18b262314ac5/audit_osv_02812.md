# [H] ALPINE-CVE-2023-28450

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-28450
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28450
Type: osv

## Affected
- Alpine:v3.14: `dnsmasq` — affected >=0 <2.86-r3
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.86-r2
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.86-r4
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.87-r2
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.89-r3
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.89-r3

## Details
An issue was discovered in Dnsmasq before 2.90. The default maximum EDNS.0 UDP packet size was set to 4096 but should be 1232 because of DNS Flag Day 2020.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28450
