# [H] ALPINE-CVE-2021-43804

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-43804
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-43804
Type: osv

## Affected
- Alpine:v3.16: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.12-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In affected versions if the incoming RTCP BYE message contains a reason's length, this declared length is not checked against the actual received packet size, potentially resulting in an out-of-bound read access. This issue affects all users that use PJMEDIA and RTCP. A malicious actor can send a RTCP BYE message with an invalid reason length. Users are advised to upgrade as soon as possible. There are no known workarounds.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-43804
