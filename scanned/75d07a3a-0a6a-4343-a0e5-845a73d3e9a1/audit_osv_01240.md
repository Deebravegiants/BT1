# [H] ALPINE-CVE-2018-7160

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7160
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7160
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.0-r0

## Details
The Node.js inspector, in 6.x and later is vulnerable to a DNS rebinding attack which could be exploited to perform remote code execution. An attack is possible from malicious websites open in a web browser on the same computer, or another computer with network access to the computer running the Node.js process. A malicious website could use a DNS rebinding attack to trick the web browser to bypass same-origin-policy checks and to allow HTTP connections to localhost or to hosts on the local network. If a Node.js process with the debug port active is running on localhost or on a host on the local network, the malicious website could connect to it as a debugger, and get full code execution access.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7160
