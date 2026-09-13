# [M] ALPINE-CVE-2020-14422

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14422
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14422
Type: osv

## Affected
- Alpine:v3.10: `python3` — affected >=0 <3.7.7-r1
- Alpine:v3.11: `python3` — affected >=0 <3.8.2-r1
- Alpine:v3.12: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.13: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.14: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.15: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.16: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.17: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.18: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.19: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.20: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.21: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.22: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.23: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.24: `python3` — affected >=0 <3.8.4-r0
- Alpine:v3.9: `python3` — affected >=0 <3.6.9-r3

## Details
Lib/ipaddress.py in Python through 3.8.3 improperly computes hash values in the IPv4Interface and IPv6Interface classes, which might allow a remote attacker to cause a denial of service if an application is affected by the performance of a dictionary containing IPv4Interface or IPv6Interface objects, and this attacker can cause many dictionary entries to be created. This is fixed in: v3.5.10, v3.5.10rc1; v3.6.12; v3.7.9; v3.8.4, v3.8.4rc1, v3.8.5, v3.8.6, v3.8.6rc1; v3.9.0, v3.9.0b4, v3.9.0b5, v3.9.0rc1, v3.9.0rc2.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14422
