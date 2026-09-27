# [H] ALPINE-CVE-2021-3121

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3121
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3121
Type: osv

## Affected
- Alpine:v3.14: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.15: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.16: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.17: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.18: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.19: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.20: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.21: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.22: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.23: `protobuf-c` — affected >=0 <1.3.2-r0
- Alpine:v3.24: `protobuf-c` — affected >=0 <1.3.2-r0

## Details
An issue was discovered in GoGo Protobuf before 1.3.2. plugin/unmarshal/unmarshal.go lacks certain index validation, aka the "skippy peanut butter" issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3121
