# [H] ALPINE-CVE-2022-42916

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42916
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42916
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.77.0 <7.80.0-r4
- Alpine:v3.16: `curl` — affected >=7.77.0 <7.83.1-r4
- Alpine:v3.17: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.18: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.19: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.20: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.21: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.22: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.23: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.24: `curl` — affected >=7.77.0 <7.86.0-r0

## Details
In curl before 7.86.0, the HSTS check could be bypassed to trick it into staying with HTTP. Using its HSTS support, curl can be instructed to use HTTPS directly (instead of using an insecure cleartext HTTP step) even when HTTP is provided in the URL. This mechanism could be bypassed if the host name in the given URL uses IDN characters that get replaced with ASCII counterparts as part of the IDN conversion, e.g., using the character UTF-8 U+3002 (IDEOGRAPHIC FULL STOP) instead of the common ASCII full stop of U+002E (.). The earliest affected version is 7.77.0 2021-05-26.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42916
