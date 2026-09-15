# [H] ALPINE-CVE-2022-41674

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41674
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41674
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
An issue was discovered in the Linux kernel before 5.19.16. Attackers able to inject WLAN frames could cause a buffer overflow in the ieee80211_bss_info_update function in net/mac80211/scan.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41674
