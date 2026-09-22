# [M] ALPINE-CVE-2019-20795

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20795
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20795
Type: osv

## Affected
- Alpine:v3.10: `iproute2` — affected >=0 <4.20.0-r2
- Alpine:v3.11: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.12: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.13: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.14: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.15: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.16: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.17: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.18: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.19: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.20: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.21: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.22: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.23: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.24: `iproute2` — affected >=0 <5.1.0-r0
- Alpine:v3.9: `iproute2` — affected >=0 <4.19.0-r1

## Details
iproute2 before 5.1.0 has a use-after-free in get_netnsid_from_name in ip/ipnetns.c. NOTE: security relevance may be limited to certain uses of setuid that, although not a default, are sometimes a configuration option offered to end users. Even when setuid is used, other factors (such as C library configuration) may block exploitability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20795
