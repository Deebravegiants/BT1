# [C] ALPINE-CVE-2022-23608

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-23608
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23608
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
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In versions up to and including 2.11.1 when in a dialog set (or forking) scenario, a hash key shared by multiple UAC dialogs can potentially be prematurely freed when one of the dialogs is destroyed . The issue may cause a dialog set to be registered in the hash table multiple times (with different hash keys) leading to undefined behavior such as dialog list collision which eventually leading to endless loop. A patch is available in commit db3235953baa56d2fb0e276ca510fefca751643f which will be included in the next release. There are no known workarounds for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23608
