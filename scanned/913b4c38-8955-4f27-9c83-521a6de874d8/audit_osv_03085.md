# [M] ALPINE-CVE-2024-40897

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-40897
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-40897
Type: osv

## Affected
- Alpine:v3.17: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.18: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.19: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.20: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.21: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.22: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.23: `orc` — affected >=0 <0.4.39-r0
- Alpine:v3.24: `orc` — affected >=0 <0.4.39-r0

## Details
Stack-based buffer overflow vulnerability exists in orcparse.c of ORC versions prior to 0.4.39. If a developer is tricked to process a specially crafted file with the affected ORC compiler, an arbitrary code may be executed on the developer's build environment. This may lead to compromise of developer machines or CI build environments.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-40897
