# [H] ALPINE-CVE-2021-3517

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3517
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2021-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3517
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.9-r5
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.10-r6
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.10-r7
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.11-r0

## Details
There is a flaw in the xml entity encoding functionality of libxml2 in versions before 2.9.11. An attacker who is able to supply a crafted file to be processed by an application linked with the affected functionality of libxml2 could trigger an out-of-bounds read. The most likely impact of this flaw is to application availability, with some potential impact to confidentiality and integrity if an attacker is able to use memory information to further exploit the application.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3517
