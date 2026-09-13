# [H] ALPINE-CVE-2018-12121

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12121
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12121
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
Node.js: All versions prior to Node.js 6.15.0, 8.14.0, 10.14.0 and 11.3.0: Denial of Service with large HTTP headers: By using a combination of many requests with maximum sized headers (almost 80 KB per connection), and carefully timed completion of the headers, it is possible to cause the HTTP server to abort from heap allocation failure. Attack potential is mitigated by the use of a load balancer or other proxy layer.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12121
