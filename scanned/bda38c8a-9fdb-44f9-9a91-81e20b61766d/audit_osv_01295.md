# [M] ALPINE-CVE-2019-0196

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-0196
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-0196
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
A vulnerability was found in Apache HTTP Server 2.4.17 to 2.4.38. Using fuzzed network input, the http/2 request handling could be made to access freed memory in string comparison when determining the method of a request and thus process the request incorrectly.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-0196
