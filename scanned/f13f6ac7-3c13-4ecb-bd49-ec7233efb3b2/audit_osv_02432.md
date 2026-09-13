# [C] ALPINE-CVE-2022-23537

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-23537
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23537
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=0 <18.20.2-r0
- Alpine:v3.18: `asterisk` — affected >=0 <18.20.2-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. Buffer overread is possible when parsing a specially crafted STUN message with unknown attribute. The vulnerability affects applications that uses STUN including PJNATH and PJSUA-LIB. The patch is available as a commit in the master branch (2.13.1).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23537
