# [C] ALPINE-CVE-2022-39269

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-39269
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-39269
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
PJSIP is a free and open source multimedia communication library written in C. When processing certain packets, PJSIP may incorrectly switch from using SRTP media transport to using basic RTP upon SRTP restart, causing the media to be sent insecurely. The vulnerability impacts all PJSIP users that use SRTP. The patch is available as commit d2acb9a in the master branch of the project and will be included in version 2.13. Users are advised to manually patch or to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-39269
