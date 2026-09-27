# [H] ALPINE-CVE-2022-24764

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24764
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24764
Type: osv

## Affected
- Alpine:v3.16: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.12.1-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.12.1-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. Versions 2.12 and prior contain a stack buffer overflow vulnerability that affects PJSUA2 users or users that call the API `pjmedia_sdp_print(), pjmedia_sdp_media_print()`. Applications that do not use PJSUA2 and do not directly call `pjmedia_sdp_print()` or `pjmedia_sdp_media_print()` should not be affected. A patch is available on the `master` branch of the `pjsip/pjproject` GitHub repository. There are currently no known workarounds.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24764
