# [H] ALPINE-CVE-2016-9594

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9594
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9594
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.11: `curl` — affected >=0 <7.52.1
- Alpine:v3.12: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.13: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.14: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.15: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.16: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.2: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.20: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.3: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.4: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.5: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.6: `curl` — affected >=0 <7.52.1
- Alpine:v3.7: `curl` — affected >=0 <7.52.1
- Alpine:v3.8: `curl` — affected >=0 <7.52.1
- Alpine:v3.9: `curl` — affected >=0 <7.52.1-r0

## Details
curl before version 7.52.1 is vulnerable to an uninitialized random in libcurl's internal function that returns a good 32bit random value.  Having a weak or virtually non-existent random value makes the operations that use it vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9594
