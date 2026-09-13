# [C] ALPINE-CVE-2022-31031

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-31031
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-31031
Type: osv

## Affected
- Alpine:v3.18: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.13-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.13-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In versions prior to and including 2.12.1 a stack buffer overflow vulnerability affects PJSIP users that use STUN in their applications, either by: setting a STUN server in their account/media config in PJSUA/PJSUA2 level, or directly using `pjlib-util/stun_simple` API. A patch is available in commit 450baca which should be included in the next release. There are no known workarounds for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-31031
