# [M] ALPINE-CVE-2019-18790

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-18790
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18790
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=13.0.0 <16.3.0-r3
- Alpine:v3.11: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <16.6.2-r0

## Details
An issue was discovered in channels/chan_sip.c in Sangoma Asterisk 13.x before 13.29.2, 16.x before 16.6.2, and 17.x before 17.0.1, and Certified Asterisk 13.21 before cert5. A SIP request can be sent to Asterisk that can change a SIP peer's IP address. A REGISTER does not need to occur, and calls can be hijacked as a result. The only thing that needs to be known is the peer's name; authentication details such as passwords do not need to be known. This vulnerability is only exploitable when the nat option is set to the default, or auto_force_rport.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18790
