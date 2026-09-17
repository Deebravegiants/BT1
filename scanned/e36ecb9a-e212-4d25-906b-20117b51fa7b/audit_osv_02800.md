# [H] ALPINE-CVE-2023-27533

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-27533
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27533
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=7.0.0 <8.0.1-r0
- Alpine:v3.15: `curl` — affected >=7.0.0 <8.0.1-r0
- Alpine:v3.16: `curl` — affected >=7.0.0 <8.0.1-r0
- Alpine:v3.17: `curl` — affected >=7.0.0 <7.88.1-r1
- Alpine:v3.18: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.19: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.20: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.21: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.22: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.23: `curl` — affected >=7.0.0 <8.0.0-r0
- Alpine:v3.24: `curl` — affected >=7.0.0 <8.0.0-r0

## Details
A vulnerability in input validation exists in curl <8.0 during communication using the TELNET protocol may allow an attacker to pass on maliciously crafted user name and "telnet options" during server negotiation. The lack of proper input scrubbing allows an attacker to send content or perform option negotiation without the application's intent. This vulnerability could be exploited if an application allows user input, thereby enabling attackers to execute arbitrary code on the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27533
