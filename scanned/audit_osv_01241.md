# [H] ALPINE-CVE-2018-7161

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7161
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7161
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.3-r0

## Details
All versions of Node.js 8.x, 9.x, and 10.x are vulnerable and the severity is HIGH. An attacker can cause a denial of service (DoS) by causing a node server providing an http2 server to crash. This can be accomplished by interacting with the http2 server in a manner that triggers a cleanup bug where objects are used in native code after they are no longer available. This has been addressed by updating the http2 implementation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7161
