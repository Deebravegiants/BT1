# [M] ALPINE-CVE-2023-24056

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-24056
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-24056
Type: osv

## Affected
- Alpine:v3.14: `pkgconf` — affected >=0 <1.7.4-r1
- Alpine:v3.15: `pkgconf` — affected >=0 <1.8.1-r0
- Alpine:v3.16: `pkgconf` — affected >=0 <1.8.1-r0
- Alpine:v3.17: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.18: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.19: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.20: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.21: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.22: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.23: `pkgconf` — affected >=0 <1.9.4-r0
- Alpine:v3.24: `pkgconf` — affected >=0 <1.9.4-r0

## Details
In pkgconf through 1.9.3, variable duplication can cause unbounded string expansion due to incorrect checks in libpkgconf/tuple.c:pkgconf_tuple_parse. For example, a .pc file containing a few hundred bytes can expand to one billion bytes.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-24056
