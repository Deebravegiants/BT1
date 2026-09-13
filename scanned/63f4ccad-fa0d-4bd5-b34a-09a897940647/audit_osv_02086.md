# [H] ALPINE-CVE-2021-22884

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-22884
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22884
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.21.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.21.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.16.0-r0

## Details
Node.js before 10.24.0, 12.21.0, 14.16.0, and 15.10.0 is vulnerable to DNS rebinding attacks as the whitelist includes “localhost6”. When “localhost6” is not present in /etc/hosts, it is just an ordinary domain that is resolved via DNS, i.e., over network. If the attacker controls the victim's DNS server or can spoof its responses, the DNS rebinding protection can be bypassed by using the “localhost6” domain. As long as the attacker uses the “localhost6” domain, they can still apply the attack described in CVE-2018-7160.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22884
