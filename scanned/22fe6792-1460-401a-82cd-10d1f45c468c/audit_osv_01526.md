# [H] ALPINE-CVE-2019-18634

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18634
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18634
Type: osv

## Affected
- Alpine:v3.10: `sudo` — affected >=1.7.1 <1.8.27-r2
- Alpine:v3.11: `sudo` — affected >=1.7.1 <1.8.29-r2
- Alpine:v3.12: `sudo` — affected >=1.7.1 <1.8.31-r0
- Alpine:v3.13: `sudo` — affected >=1.7.1 <1.8.31-r0
- Alpine:v3.14: `sudo` — affected >=1.7.1 <1.8.31-r0
- Alpine:v3.15: `sudo` — affected >=1.7.1 <1.8.31-r0
- Alpine:v3.8: `sudo` — affected >=1.7.1 <1.8.23-r4
- Alpine:v3.9: `sudo` — affected >=1.7.1 <1.8.25_p1-r3

## Details
In Sudo before 1.8.26, if pwfeedback is enabled in /etc/sudoers, users can trigger a stack-based buffer overflow in the privileged sudo process. (pwfeedback is a default setting in Linux Mint and elementary OS; however, it is NOT the default for upstream and many other packages, and would exist only if enabled by an administrator.) The attacker needs to deliver a long string to the stdin of getln() in tgetpass.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18634
