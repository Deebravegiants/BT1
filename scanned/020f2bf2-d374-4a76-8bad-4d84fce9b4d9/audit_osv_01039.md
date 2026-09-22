# [C] ALPINE-CVE-2018-16842

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-16842
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16842
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.11: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.12: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.13: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.14: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.15: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.16: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.17: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.18: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.19: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.20: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.21: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.22: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.23: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.24: `curl` — affected >=7.14.1 <7.62.0-r0
- Alpine:v3.5: `curl` — affected >=7.14.1 <7.61.1-r1
- Alpine:v3.6: `curl` — affected >=7.14.1 <7.61.1-r1
- Alpine:v3.7: `curl` — affected >=7.14.1 <7.61.1-r1
- Alpine:v3.8: `curl` — affected >=7.14.1 <7.61.1-r1
- Alpine:v3.9: `curl` — affected >=7.14.1 <7.62.0-r0

## Details
Curl versions 7.14.1 through 7.61.1 are vulnerable to a heap-based buffer over-read in the tool_msgs.c:voutf() function that may result in information exposure and denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16842
