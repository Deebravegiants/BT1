# [H] ALPINE-CVE-2020-8616

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8616
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8616
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
A malicious actor who intentionally exploits this lack of effective limitation on the number of fetches performed when processing referrals can, through the use of specially crafted referrals, cause a recursing server to issue a very large number of fetches in an attempt to process the referral. This has at least two potential effects: The performance of the recursing server can potentially be degraded by the additional work required to perform these fetches, and The attacker can exploit this behavior to use the recursing server as a reflector in a reflection attack with a high amplification factor.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8616
