# [C] ALPINE-CVE-2021-31535

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-31535
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31535
Type: osv

## Affected
- Alpine:v3.10: `libx11` — affected >=0 <1.6.12-r1
- Alpine:v3.11: `libx11` — affected >=0 <1.6.12-r1
- Alpine:v3.12: `libx11` — affected >=0 <1.6.12-r1
- Alpine:v3.13: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.14: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.15: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.16: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.7.1-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.7.1-r0

## Details
LookupCol.c in X.Org X through X11R7.7 and libX11 before 1.7.1 might allow remote attackers to execute arbitrary code. The libX11 XLookupColor request (intended for server-side color lookup) contains a flaw allowing a client to send color-name requests with a name longer than the maximum size allowed by the protocol (and also longer than the maximum packet size for normal-sized packets). The user-controlled data exceeding the maximum size is then interpreted by the server as additional X protocol requests and executed, e.g., to disable X server authorization completely. For example, if the victim encounters malicious terminal control sequences for color codes, then the attacker may be able to take full control of the running graphical session.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31535
