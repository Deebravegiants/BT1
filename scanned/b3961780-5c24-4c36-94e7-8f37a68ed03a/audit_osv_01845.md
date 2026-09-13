# [H] ALPINE-CVE-2020-18032

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-18032
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-18032
Type: osv

## Affected
- Alpine:v3.11: `graphviz` — affected >=0 <2.42.3-r1
- Alpine:v3.12: `graphviz` — affected >=0 <2.44.0-r1
- Alpine:v3.13: `graphviz` — affected >=0 <2.44.0-r2
- Alpine:v3.14: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.15: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.16: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.17: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.18: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.19: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.20: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.21: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.22: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.23: `graphviz` — affected >=0 <2.46.0-r0
- Alpine:v3.24: `graphviz` — affected >=0 <2.46.0-r0

## Details
Buffer Overflow in Graphviz Graph Visualization Tools from commit ID f8b9e035 and earlier allows remote attackers to execute arbitrary code or cause a denial of service (application crash) by loading a crafted file into the "lib/common/shapes.c" component.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-18032
