# [H] ALPINE-CVE-2021-28041

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28041
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28041
Type: osv

## Affected
- Alpine:v3.12: `openssh` — affected >=8.2 <8.3_p1-r2
- Alpine:v3.13: `openssh` — affected >=8.2 <8.4_p1-r1
- Alpine:v3.14: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.15: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.16: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.17: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.18: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.19: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.20: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.21: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.22: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.23: `openssh` — affected >=8.2 <8.5_p1-r0
- Alpine:v3.24: `openssh` — affected >=8.2 <8.5_p1-r0

## Details
ssh-agent in OpenSSH before 8.5 has a double free that may be relevant in a few less-common scenarios, such as unconstrained agent-socket access on a legacy operating system, or the forwarding of an agent to an attacker-controlled host.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28041
