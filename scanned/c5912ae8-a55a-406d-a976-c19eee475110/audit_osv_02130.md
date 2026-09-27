# [H] ALPINE-CVE-2021-26717

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-26717
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-26717
Type: osv

## Affected
- Alpine:v3.12: `asterisk` — affected >=16.0.0 <16.16.1-r0
- Alpine:v3.13: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.14: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.15: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.16: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.17: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.18: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.19: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.20: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.21: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.22: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.23: `asterisk` — affected >=16.0.0 <18.2.1-r0
- Alpine:v3.24: `asterisk` — affected >=16.0.0 <18.2.1-r0

## Details
An issue was discovered in Sangoma Asterisk 16.x before 16.16.1, 17.x before 17.9.2, and 18.x before 18.2.1 and Certified Asterisk before 16.8-cert6. When re-negotiating for T.38, if the initial remote response was delayed just enough, Asterisk would send both audio and T.38 in the SDP. If this happened, and the remote responded with a declined T.38 stream, then Asterisk would crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-26717
