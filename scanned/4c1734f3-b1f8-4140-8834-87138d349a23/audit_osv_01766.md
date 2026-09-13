# [M] ALPINE-CVE-2020-14347

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14347
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14347
Type: osv

## Affected
- Alpine:v3.10: `xorg-server` — affected >=0 <1.20.5-r1
- Alpine:v3.11: `xorg-server` — affected >=0 <1.20.6-r1
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.8-r4

## Details
A flaw was found in the way xserver memory was not properly initialized. This could leak parts of server memory to the X client. In cases where Xorg server runs with elevated privileges, this could result in possible ASLR bypass. Xorg-server before version 1.20.9 is vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14347
