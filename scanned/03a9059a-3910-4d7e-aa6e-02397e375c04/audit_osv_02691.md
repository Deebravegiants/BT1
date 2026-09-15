# [M] ALPINE-CVE-2022-42721

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42721
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42721
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
A list management bug in BSS handling in the mac80211 stack in the Linux kernel 5.1 through 5.19.x before 5.19.16 could be used by local attackers (able to inject WLAN frames) to corrupt a linked list and, in turn, potentially execute code.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42721
