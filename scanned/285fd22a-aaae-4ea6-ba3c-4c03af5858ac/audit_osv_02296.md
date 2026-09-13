# [H] ALPINE-CVE-2021-41141

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41141
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41141
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
PJSIP is a free and open source multimedia communication library written in the C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In various parts of PJSIP, when error/failure occurs, it is found that the function returns without releasing the currently held locks. This could result in a system deadlock, which cause a denial of service for the users. No release has yet been made which contains the linked fix commit. All versions up to an including 2.11.1 are affected. Users may need to manually apply the patch.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41141
