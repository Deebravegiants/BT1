# [M] ALPINE-CVE-2022-41861

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-41861
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41861
Type: osv

## Affected
- Alpine:v3.15: `freeradius` — affected >=0 <3.0.26-r0
- Alpine:v3.16: `freeradius` — affected >=0 <3.0.26-r0

## Details
A flaw was found in freeradius. A malicious RADIUS client or home server can send a malformed abinary attribute which can cause the server to crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41861
