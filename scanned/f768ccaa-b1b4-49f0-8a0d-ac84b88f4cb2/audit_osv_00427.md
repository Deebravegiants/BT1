# [C] ALPINE-CVE-2017-12182

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-12182
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12182
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
xorg-x11-server before 1.19.5 was missing length validation in XFree86 DRI extension allowing malicious X client to cause X server to crash or possibly execute arbitrary code.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12182
