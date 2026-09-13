# [M] ALPINE-CVE-2020-21913

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-21913
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-21913
Type: osv

## Affected
- Alpine:v3.15: `icu` — affected >=0 <66.1-r0
- Alpine:v3.16: `icu` — affected >=0 <66.1-r0
- Alpine:v3.17: `icu` — affected >=0 <66.1-r0
- Alpine:v3.18: `icu` — affected >=0 <66.1-r0
- Alpine:v3.19: `icu` — affected >=0 <66.1-r0
- Alpine:v3.20: `icu` — affected >=0 <66.1-r0
- Alpine:v3.21: `icu` — affected >=0 <66.1-r0
- Alpine:v3.22: `icu` — affected >=0 <66.1-r0
- Alpine:v3.23: `icu` — affected >=0 <66.1-r0
- Alpine:v3.24: `icu` — affected >=0 <66.1-r0

## Details
International Components for Unicode (ICU-20850) v66.1 was discovered to contain a use after free bug in the pkg_createWithAssemblyCode function in the file tools/pkgdata/pkgdata.cpp.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-21913
