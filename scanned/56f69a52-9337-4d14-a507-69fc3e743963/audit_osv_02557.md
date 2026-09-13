# [H] ALPINE-CVE-2022-31001

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-31001
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-31001
Type: osv

## Affected
- Alpine:v3.14: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.15: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.16: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.17: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.18: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.19: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.20: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.21: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.22: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.23: `sofia-sip` — affected >=0 <1.13.8-r0
- Alpine:v3.24: `sofia-sip` — affected >=0 <1.13.8-r0

## Details
Sofia-SIP is an open-source Session Initiation Protocol (SIP) User-Agent library. Prior to version 1.13.8, an attacker can send a message with evil sdp to FreeSWITCH, which may cause crash. This type of crash may be caused by `#define MATCH(s, m) (strncmp(s, m, n = sizeof(m) - 1) == 0)`, which will make `n` bigger and trigger out-of-bound access when `IS_NON_WS(s[n])`. Version 1.13.8 contains a patch for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-31001
