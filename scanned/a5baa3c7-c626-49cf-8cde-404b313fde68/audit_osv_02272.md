# [C] ALPINE-CVE-2021-37706

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-37706
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37706
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
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In affected versions if the incoming STUN message contains an ERROR-CODE attribute, the header length is not checked before performing a subtraction operation, potentially resulting in an integer underflow scenario. This issue affects all users that use STUN. A malicious actor located within the victim’s network may forge and send a specially crafted UDP (STUN) message that could remotely execute arbitrary code on the victim’s machine. Users are advised to upgrade as soon as possible. There are no known workarounds.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37706
