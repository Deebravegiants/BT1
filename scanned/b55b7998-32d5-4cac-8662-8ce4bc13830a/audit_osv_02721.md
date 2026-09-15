# [C] ALPINE-CVE-2022-44640

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-44640
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-44640
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0

## Details
Heimdal before 7.7.1 allows remote attackers to execute arbitrary code because of an invalid free in the ASN.1 codec used by the Key Distribution Center (KDC).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-44640
