# [H] ALPINE-CVE-2019-25051

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-25051
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-25051
Type: osv

## Affected
- Alpine:v3.11: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.12: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.13: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.14: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.15: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.16: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.17: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.18: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.19: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.20: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.21: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.22: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.23: `aspell` — affected >=0 <0.60.8-r1
- Alpine:v3.24: `aspell` — affected >=0 <0.60.8-r1

## Details
objstack in GNU Aspell 0.60.8 has a heap-based buffer overflow in acommon::ObjStack::dup_top (called from acommon::StringMap::add and acommon::Config::lookup_list).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-25051
