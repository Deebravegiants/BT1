# [M] ALPINE-CVE-2022-1097

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-1097
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1097
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.68.3-r0
- Alpine:v3.19: `nss` — affected >=0 <3.76.1-r0
- Alpine:v3.20: `nss` — affected >=0 <3.76.1-r0
- Alpine:v3.21: `nss` — affected >=0 <3.76.1-r0
- Alpine:v3.22: `nss` — affected >=0 <3.76.1-r0
- Alpine:v3.23: `nss` — affected >=0 <3.76.1-r0
- Alpine:v3.24: `nss` — affected >=0 <3.76.1-r0

## Details
<code>NSSToken</code> objects were referenced via direct points, and could have been accessed in an unsafe way on different threads, leading to a use-after-free and potentially exploitable crash. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1097
