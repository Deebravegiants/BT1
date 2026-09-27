# [C] ALPINE-CVE-2022-24786

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-24786
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24786
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
PJSIP is a free and open source multimedia communication library written in C. PJSIP versions 2.12 and prior do not parse incoming RTCP feedback RPSI (Reference Picture Selection Indication) packet, but any app that directly uses pjmedia_rtcp_fb_parse_rpsi() will be affected. A patch is available in the `master` branch of the `pjsip/pjproject` GitHub repository. There are currently no known workarounds.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24786
