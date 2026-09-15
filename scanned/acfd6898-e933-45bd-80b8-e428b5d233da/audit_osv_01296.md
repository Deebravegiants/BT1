# [M] ALPINE-CVE-2019-0197

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-0197
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-0197
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.39-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.39-r0

## Details
A vulnerability was found in Apache HTTP Server 2.4.34 to 2.4.38. When HTTP/2 was enabled for a http: host or H2Upgrade was enabled for h2 on a https: host, an Upgrade request from http/1.1 to http/2 that was not the first request on a connection could lead to a misconfiguration and crash. Server that never enabled the h2 protocol or that only enabled it for https: and did not set "H2Upgrade on" are unaffected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-0197
