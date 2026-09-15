# [H] ALPINE-CVE-2017-13723

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13723
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13723
Type: osv

## Affected
- Alpine:v3.10: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.11: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.12: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.6: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.7: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.8: `xorg-server` — affected >=0 <1.19.5-r0
- Alpine:v3.9: `xorg-server` — affected >=0 <1.19.5-r0

## Details
In X.Org Server (aka xserver and xorg-server) before 1.19.4, a local attacker authenticated to the X server could overflow a global buffer, causing crashes of the X server or potentially other problems by injecting large or malformed XKB related atoms and accessing them via xkbcomp.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13723
