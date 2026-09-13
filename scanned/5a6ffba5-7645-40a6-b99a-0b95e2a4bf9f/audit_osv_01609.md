# [H] ALPINE-CVE-2019-5737

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5737
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5737
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <10.15.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <10.15.3-r0

## Details
In Node.js including 6.x before 6.17.0, 8.x before 8.15.1, 10.x before 10.15.2, and 11.x before 11.10.1, an attacker can cause a Denial of Service (DoS) by establishing an HTTP or HTTPS connection in keep-alive mode and by sending headers very slowly. This keeps the connection and associated resources alive for a long period of time. Potential attacks are mitigated by the use of a load balancer or other proxy layer. This vulnerability is an extension of CVE-2018-12121, addressed in November and impacts all active Node.js release lines including 6.x before 6.17.0, 8.x before 8.15.1, 10.x before 10.15.2, and 11.x before 11.10.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5737
