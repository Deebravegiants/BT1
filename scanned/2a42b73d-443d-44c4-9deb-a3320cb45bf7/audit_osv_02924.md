# [H] ALPINE-CVE-2023-49294

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-49294
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49294
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.18: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.19: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.20: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.21: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.22: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.23: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.24: `asterisk` — affected >=19.0.0 <20.5.1-r0

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In Asterisk prior to versions 18.20.1, 20.5.1, and 21.0.1, as well as certified-asterisk prior to 18.9-cert6, it is possible to read any arbitrary file even when the `live_dangerously` is not enabled. This allows arbitrary files to be read. Asterisk versions 18.20.1, 20.5.1, and 21.0.1, as well as certified-asterisk prior to 18.9-cert6, contain a fix for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49294
