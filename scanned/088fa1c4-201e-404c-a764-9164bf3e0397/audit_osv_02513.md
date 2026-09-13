# [M] ALPINE-CVE-2022-27776

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-27776
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27776
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=0 <7.79.1-r1
- Alpine:v3.13: `curl` — affected >=0 <7.79.1-r1
- Alpine:v3.14: `curl` — affected >=0 <7.79.1-r1
- Alpine:v3.15: `curl` — affected >=0 <7.80.0-r1
- Alpine:v3.16: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.83.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.83.0-r0

## Details
A insufficiently protected credentials vulnerability in fixed in curl 7.83.0 might leak authentication or cookie header data on HTTP redirects to the same host but another port number.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27776
