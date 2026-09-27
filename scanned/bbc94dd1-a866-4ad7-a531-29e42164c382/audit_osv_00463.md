# [M] ALPINE-CVE-2017-13721

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-13721
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13721
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
In X.Org Server (aka xserver and xorg-server) before 1.19.4, an attacker authenticated to an X server with the X shared memory extension enabled can cause aborts of the X server or replace shared memory segments of other X clients in the same session.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13721
