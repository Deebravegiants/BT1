# [M] ALPINE-CVE-2018-20685

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20685
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20685
Type: osv

## Affected
- Alpine:v3.10: `dropbear` — affected >=0 <2019.78-r1
- Alpine:v3.11: `dropbear` — affected >=0 <2019.78-r1
- Alpine:v3.12: `dropbear` — affected >=0 <2019.78-r1
- Alpine:v3.13: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.14: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.15: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.16: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.17: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.18: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.19: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.20: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.21: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.22: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.23: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.24: `dropbear` — affected >=0 <2020.79-r0
- Alpine:v3.9: `dropbear` — affected >=0 <2018.76-r3
- Alpine:v3.10: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.11: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.12: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.13: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.14: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.15: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.16: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.17: `openssh` — affected >=0 <7.9_p1-r3
- Alpine:v3.18: `openssh` — affected >=0 <7.9_p1-r3

## Details
In OpenSSH 7.9, scp.c in the scp client allows remote SSH servers to bypass intended access restrictions via the filename of . or an empty filename. The impact is modifying the permissions of the target directory on the client side.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20685
