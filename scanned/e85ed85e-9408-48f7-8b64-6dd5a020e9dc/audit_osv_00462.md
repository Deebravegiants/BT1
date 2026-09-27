# [H] ALPINE-CVE-2017-13704

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13704
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13704
Type: osv

## Affected
- Alpine:v3.10: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.11: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.12: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.13: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.14: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.7: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.8: `dnsmasq` — affected >=0 <2.78-r0
- Alpine:v3.9: `dnsmasq` — affected >=0 <2.78-r0

## Details
In dnsmasq before 2.78, if the DNS packet size does not match the expected size, the size parameter in a memset call gets a negative value. As it is an unsigned value, memset ends up writing up to 0xffffffff zero's (0xffffffffffffffff in 64 bit platforms), making dnsmasq crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13704
