# [M] ALPINE-CVE-2023-43786

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-43786
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43786
Type: osv

## Affected
- Alpine:v3.16: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.8.7-r0

## Details
A vulnerability was found in libX11 due to an infinite loop within the PutSubImage() function. This flaw allows a local user to consume all available system resources and cause a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43786
