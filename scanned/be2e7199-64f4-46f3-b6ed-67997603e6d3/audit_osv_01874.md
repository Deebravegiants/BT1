# [M] ALPINE-CVE-2020-24977

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-24977
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-09-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-24977
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.9-r4
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.10-r4
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.9: `libxml2` — affected >=0 <2.9.9-r3

## Details
GNOME project libxml2 v2.9.10 has a global buffer over-read vulnerability in xmlEncodeEntitiesInternal at libxml2/entities.c. The issue has been fixed in commit 50f06b3e.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-24977
