# [H] ALPINE-CVE-2022-24793

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24793
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24793
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
PJSIP is a free and open source multimedia communication library written in C. A buffer overflow vulnerability in versions 2.12 and prior affects applications that use PJSIP DNS resolution. It doesn't affect PJSIP users who utilize an external resolver. This vulnerability is related to CVE-2023-27585. The difference is that this issue is in parsing the query record `parse_rr()`, while the issue in CVE-2023-27585 is in `parse_query()`. A patch is available in the `master` branch of the `pjsip/pjproject` GitHub repository. A workaround is to disable DNS resolution in PJSIP config (by setting `nameserver_count` to zero) or use an external resolver instead.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24793
