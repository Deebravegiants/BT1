# [H] ALPINE-CVE-2024-6387

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6387
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6387
Type: osv

## Affected
- Alpine:v3.17: `openssh` — affected >=8.6 <9.1_p1-r6
- Alpine:v3.18: `openssh` — affected >=8.6 <9.3_p2-r2
- Alpine:v3.19: `openssh` — affected >=8.6 <9.6_p1-r1
- Alpine:v3.20: `openssh` — affected >=8.6 <9.7_p1-r4
- Alpine:v3.21: `openssh` — affected >=8.6 <9.8_p1-r0
- Alpine:v3.22: `openssh` — affected >=8.6 <9.8_p1-r0
- Alpine:v3.23: `openssh` — affected >=8.6 <9.8_p1-r0
- Alpine:v3.24: `openssh` — affected >=8.6 <9.8_p1-r0

## Details
A security regression (CVE-2006-5051) was discovered in OpenSSH's server (sshd). There is a race condition which can lead sshd to handle some signals in an unsafe manner. An unauthenticated, remote attacker may be able to trigger it by failing to authenticate within a set time period.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6387
