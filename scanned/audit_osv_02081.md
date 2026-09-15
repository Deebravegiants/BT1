# [M] ALPINE-CVE-2021-21375

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-21375
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-21375
Type: osv

## Affected
- Alpine:v3.14: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.15: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.16: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.11-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In PJSIP version 2.10 and earlier, after an initial INVITE has been sent, when two 183 responses are received, with the first one causing negotiation failure, a crash will occur. This results in a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-21375
