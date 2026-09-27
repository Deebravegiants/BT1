# [M] ALPINE-CVE-2018-12123

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12123
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12123
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.14.0-r0
- Alpine:v3.9: `nodejs` — affected >=0 <10.14.0-r0

## Details
Node.js: All versions prior to Node.js 6.15.0, 8.14.0, 10.14.0 and 11.3.0: Hostname spoofing in URL parser for javascript protocol: If a Node.js application is using url.parse() to determine the URL hostname, that hostname can be spoofed by using a mixed case "javascript:" (e.g. "javAscript:") protocol (other protocols are not affected). If security decisions are made about the URL based on the hostname, they may be incorrect.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12123
