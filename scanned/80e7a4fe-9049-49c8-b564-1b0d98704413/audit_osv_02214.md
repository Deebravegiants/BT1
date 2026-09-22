# [M] ALPINE-CVE-2021-32686

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-32686
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32686
Type: osv

## Affected
- Alpine:v3.14: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.15: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.16: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.11.1-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.11.1-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In PJSIP before version 2.11.1, there are a couple of issues found in the SSL socket. First, a race condition between callback and destroy, due to the accepted socket having no group lock. Second, the SSL socket parent/listener may get destroyed during handshake. Both issues were reported to happen intermittently in heavy load TLS connections. They cause a crash, resulting in a denial of service. These are fixed in version 2.11.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32686
