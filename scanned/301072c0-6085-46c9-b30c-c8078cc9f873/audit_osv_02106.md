# [M] ALPINE-CVE-2021-23336

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-23336
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23336
Type: osv

## Affected
- Alpine:v3.12: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.13: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.14: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.15: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.16: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.17: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.18: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.19: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.20: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.21: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.22: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.23: `python3` — affected >=0 <3.8.8-r0
- Alpine:v3.24: `python3` — affected >=0 <3.8.8-r0

## Details
The package python/cpython from 0 and before 3.6.13, from 3.7.0 and before 3.7.10, from 3.8.0 and before 3.8.8, from 3.9.0 and before 3.9.2 are vulnerable to Web Cache Poisoning via urllib.parse.parse_qsl and urllib.parse.parse_qs by using a vector called parameter cloaking. When the attacker can separate query parameters using a semicolon (;), they can cause a difference in the interpretation of the request between the proxy (running with default configuration) and the server. This can result in malicious requests being cached as completely safe ones, as the proxy would usually not see the semicolon as a separator, and therefore would not include it in a cache key of an unkeyed parameter.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23336
