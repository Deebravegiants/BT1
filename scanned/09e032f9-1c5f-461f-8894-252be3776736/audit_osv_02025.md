# [M] ALPINE-CVE-2020-8617

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8617
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8617
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.11: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.12: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.13: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.14: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.15: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.14.12-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.14.12-r0

## Details
Using a specially-crafted message, an attacker may potentially cause a BIND server to reach an inconsistent state if the attacker knows (or successfully guesses) the name of a TSIG key used by the server. Since BIND, by default, configures a local session key even on servers whose configuration does not otherwise make use of it, almost all current BIND servers are vulnerable. In releases of BIND dating from March 2018 and after, an assertion check in tsig.c detects this inconsistent state and deliberately exits. Prior to the introduction of the check the server would continue operating in an inconsistent state, with potentially harmful results.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8617
