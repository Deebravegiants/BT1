# [H] ALPINE-CVE-2022-24792

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24792
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24792
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
PJSIP is a free and open source multimedia communication library written in C. A denial-of-service vulnerability affects applications on a 32-bit systems that use PJSIP versions 2.12 and prior to play/read invalid WAV files. The vulnerability occurs when reading WAV file data chunks with length greater than 31-bit integers. The vulnerability does not affect 64-bit apps and should not affect apps that only plays trusted WAV files. A patch is available on the `master` branch of the `pjsip/project` GitHub repository. As a workaround, apps can reject a WAV file received from an unknown source or validate the file first.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24792
