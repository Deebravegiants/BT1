# [M] ALPINE-CVE-2022-42705

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42705
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42705
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=16.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.18: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.19: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.20: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.21: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.22: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.23: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.24: `asterisk` — affected >=16.0.0 <18.15.1-r0

## Details
A use-after-free in res_pjsip_pubsub.c in Sangoma Asterisk 16.28, 18.14, 19.6, and certified/18.9-cert2 may allow a remote authenticated attacker to crash Asterisk (denial of service) by performing activity on a subscription via a reliable transport at the same time that Asterisk is also performing activity on that subscription.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42705
