# [H] ALPINE-CVE-2017-11610

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11610
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11610
Type: osv

## Affected
- Alpine:v3.10: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.11: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.12: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.13: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.14: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.15: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.16: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.17: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.18: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.19: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.20: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.21: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.22: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.23: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.24: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.3: `supervisor` — affected >=0 <3.1.4-r0
- Alpine:v3.4: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.5: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.6: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.7: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.8: `supervisor` — affected >=0 <3.2.4-r0
- Alpine:v3.9: `supervisor` — affected >=0 <3.2.4-r0

## Details
The XML-RPC server in supervisor before 3.0.1, 3.1.x before 3.1.4, 3.2.x before 3.2.4, and 3.3.x before 3.3.3 allows remote authenticated users to execute arbitrary commands via a crafted XML-RPC request, related to nested supervisord namespace lookups.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11610
