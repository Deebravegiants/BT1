# [H] ALPINE-CVE-2022-42719

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42719
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42719
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
A use-after-free in the mac80211 stack when parsing a multi-BSSID element in the Linux kernel 5.2 through 5.19.x before 5.19.16 could be used by attackers (able to inject WLAN frames) to crash the kernel and potentially execute code.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42719
