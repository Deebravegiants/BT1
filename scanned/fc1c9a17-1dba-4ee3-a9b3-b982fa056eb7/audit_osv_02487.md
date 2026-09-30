# [C] ALPINE-CVE-2022-26499

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-26499
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26499
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.17: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.18: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.19: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.20: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.21: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.22: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.23: `asterisk` — affected >=16.15.0 <18.11.2-r0
- Alpine:v3.24: `asterisk` — affected >=16.15.0 <18.11.2-r0

## Details
An SSRF issue was discovered in Asterisk through 19.x. When using STIR/SHAKEN, it's possible to send arbitrary requests (such as GET) to interfaces such as localhost by using the Identity header. This is fixed in 16.25.2, 18.11.2, and 19.3.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26499
