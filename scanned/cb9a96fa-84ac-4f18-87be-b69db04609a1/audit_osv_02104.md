# [M] ALPINE-CVE-2021-23222

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-23222
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23222
Type: osv

## Affected
- Alpine:v3.11: `postgresql` — affected >=9.6 <12.9-r0
- Alpine:v3.12: `postgresql` — affected >=9.6 <12.9-r0
- Alpine:v3.13: `postgresql` — affected >=9.6 <13.5-r0
- Alpine:v3.14: `postgresql` — affected >=9.6 <13.5-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.5-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.5-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.1-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.1-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.1-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.1-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <14.1-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <14.1-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <14.1-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <14.1-r0

## Details
A man-in-the-middle attacker can inject false responses to the client's first few queries, despite the use of SSL certificate verification and encryption.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23222
