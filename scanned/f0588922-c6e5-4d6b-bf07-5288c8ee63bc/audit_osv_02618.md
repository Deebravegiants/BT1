# [H] ALPINE-CVE-2022-37325

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-37325
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-37325
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=16.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.18: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.19: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.20: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.21: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.22: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.23: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.24: `asterisk` — affected >=16.0.0 <18.15.1-r0

## Details
In Sangoma Asterisk through 16.28.0, 17.x and 18.x through 18.14.0, and 19.x through 19.6.0, an incoming Setup message to addons/ooh323c/src/ooq931.c with a malformed Calling or Called Party IE can cause a crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-37325
