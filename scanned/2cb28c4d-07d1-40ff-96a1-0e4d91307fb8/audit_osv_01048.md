# [M] ALPINE-CVE-2018-16876

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16876
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16876
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.5.0 <2.7.9-r0
- Alpine:v3.11: `ansible` — affected >=2.5.0 <2.7.9-r0
- Alpine:v3.12: `ansible` — affected >=2.5.0 <2.7.9-r0
- Alpine:v3.8: `ansible` — affected >=2.5.0 <2.5.14-r0
- Alpine:v3.9: `ansible` — affected >=2.5.0 <2.7.5-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.7.9-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.7.9-r0

## Details
ansible before versions 2.5.14, 2.6.11, 2.7.5 is vulnerable to a information disclosure flaw in vvv+ mode with no_log on that can lead to leakage of sensible data.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16876
