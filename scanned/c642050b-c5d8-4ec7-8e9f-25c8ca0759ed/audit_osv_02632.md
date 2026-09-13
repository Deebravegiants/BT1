# [C] ALPINE-CVE-2022-39244

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-39244
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-39244
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
PJSIP is a free and open source multimedia communication library written in C. In versions of PJSIP prior to 2.13 the PJSIP parser, PJMEDIA RTP decoder, and PJMEDIA SDP parser are affeced by a buffer overflow vulnerability. Users connecting to untrusted clients are at risk. This issue has been patched and is available as commit c4d3498 in the master branch and will be included in releases 2.13 and later. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-39244
