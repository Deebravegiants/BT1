# [H] ALPINE-CVE-2022-38177

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-38177
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-38177
Type: osv

## Affected
- Alpine:v3.13: `bind` — affected >=9.8.4 <9.16.33-r0
- Alpine:v3.14: `bind` — affected >=9.8.4 <9.16.33-r0
- Alpine:v3.15: `bind` — affected >=9.8.4 <9.16.33-r0
- Alpine:v3.16: `bind` — affected >=9.8.4 <9.16.33-r0
- Alpine:v3.17: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.18: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.19: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.20: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.21: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.22: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.23: `bind` — affected >=9.8.4 <9.18.7-r0
- Alpine:v3.24: `bind` — affected >=9.8.4 <9.18.7-r0

## Details
By spoofing the target resolver with responses that have a malformed ECDSA signature, an attacker can trigger a small memory leak. It is possible to gradually erode available memory to the point where named crashes for lack of resources.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-38177
