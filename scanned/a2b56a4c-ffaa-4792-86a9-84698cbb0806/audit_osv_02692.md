# [M] ALPINE-CVE-2022-42722

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42722
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42722
Type: osv

## Affected
- Alpine:v3.15: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.16: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.17: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.18: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.19: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.20: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.21: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.22: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.23: `linux-lts` — affected >=0 <5.15.74-r0
- Alpine:v3.24: `linux-lts` — affected >=0 <5.15.74-r0

## Details
In the Linux kernel 5.8 through 5.19.x before 5.19.16, local attackers able to inject WLAN frames into the mac80211 stack could cause a NULL pointer dereference denial-of-service attack against the beacon protection of P2P devices.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42722
