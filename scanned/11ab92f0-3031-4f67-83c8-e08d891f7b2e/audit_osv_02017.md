# [M] ALPINE-CVE-2020-8287

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8287
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8287
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.15.4-r0

## Details
Node.js versions before 10.23.1, 12.20.1, 14.15.4, 15.5.1 allow two copies of a header field in an HTTP request (for example, two Transfer-Encoding header fields). In this case, Node.js identifies the first header field and ignores the second. This can lead to HTTP Request Smuggling.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8287
