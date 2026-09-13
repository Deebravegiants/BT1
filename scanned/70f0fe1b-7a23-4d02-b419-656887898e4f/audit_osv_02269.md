# [M] ALPINE-CVE-2021-37600

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-37600
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37600
Type: osv

## Affected
- Alpine:v3.14: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.15: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.16: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.17: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.18: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.19: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.20: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.21: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.22: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.23: `util-linux` — affected >=0 <2.37.2-r0
- Alpine:v3.24: `util-linux` — affected >=0 <2.37.2-r0

## Details
An integer overflow in util-linux through 2.37.1 can potentially cause a buffer overflow if an attacker were able to use system resources in a way that leads to a large number in the /proc/sysvipc/sem file. NOTE: this is unexploitable in GNU C Library environments, and possibly in all realistic environments.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37600
