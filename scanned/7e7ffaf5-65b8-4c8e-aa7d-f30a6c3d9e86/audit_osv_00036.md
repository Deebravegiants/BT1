# [M] ALPINE-CVE-2016-10011

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10011
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10011
Type: osv

## Affected
- Alpine:v3.10: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.11: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.12: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.13: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.14: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.15: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.16: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.17: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.18: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.19: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.2: `openssh` — affected >=0 <6.8_p1-r9
- Alpine:v3.20: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.21: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.22: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.23: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.24: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.3: `openssh` — affected >=0 <7.2_p2-r3
- Alpine:v3.4: `openssh` — affected >=0 <7.2_p2-r4
- Alpine:v3.5: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.6: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.7: `openssh` — affected >=0 <7.5_p1-r8
- Alpine:v3.8: `openssh` — affected >=0 <7.4_p1-r0
- Alpine:v3.9: `openssh` — affected >=0 <7.4_p1-r0

## Details
authfile.c in sshd in OpenSSH before 7.4 does not properly consider the effects of realloc on buffer contents, which might allow local users to obtain sensitive private-key information by leveraging access to a privilege-separated child process.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10011
