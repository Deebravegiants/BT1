# [H] ALPINE-CVE-2023-27585

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-27585
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27585
Type: osv

## Affected
- Alpine:v3.18: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.13.1-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.13.1-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. A buffer overflow vulnerability in versions 2.13 and prior affects applications that use PJSIP DNS resolver. It doesn't affect PJSIP users who do not utilise PJSIP DNS resolver. This vulnerability is related to CVE-2022-24793. The difference is that this issue is in parsing the query record `parse_query()`, while the issue in CVE-2022-24793 is in `parse_rr()`. A patch is available as commit `d1c5e4d` in the `master` branch. A workaround is to disable DNS resolution in PJSIP config (by setting `nameserver_count` to zero) or use an external resolver implementation instead.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27585
