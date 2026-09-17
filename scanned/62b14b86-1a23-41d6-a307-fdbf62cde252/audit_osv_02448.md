# [C] ALPINE-CVE-2022-24754

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-24754
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24754
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
PJSIP is a free and open source multimedia communication library written in C language. In versions prior to and including 2.12 PJSIP there is a stack-buffer overflow vulnerability which only impacts PJSIP users who accept hashed digest credentials (credentials with data_type `PJSIP_CRED_DATA_DIGEST`). This issue has been patched in the master branch of the PJSIP repository and will be included with the next release. Users unable to upgrade need to check that the hashed digest data length must be equal to `PJSIP_MD5STRLEN` before passing to PJSIP.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24754
