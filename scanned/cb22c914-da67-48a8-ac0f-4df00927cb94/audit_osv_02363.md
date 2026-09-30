# [M] ALPINE-CVE-2022-0529

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-0529
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0529
Type: osv

## Affected
- Alpine:v3.17: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.18: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.19: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.20: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.21: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.22: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.23: `unzip` — affected >=0 <6.0-r11
- Alpine:v3.24: `unzip` — affected >=0 <6.0-r11

## Details
A flaw was found in Unzip. The vulnerability occurs during the conversion of a wide string to a local string that leads to a heap of out-of-bound write. This flaw allows an attacker to input a specially crafted zip file, leading to a crash or code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0529
