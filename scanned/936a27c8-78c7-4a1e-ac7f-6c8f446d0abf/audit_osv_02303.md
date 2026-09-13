# [H] ALPINE-CVE-2021-41617

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41617
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41617
Type: osv

## Affected
- Alpine:v3.11: `openssh` — affected >=6.2 <8.1_p1-r1
- Alpine:v3.12: `openssh` — affected >=6.2 <8.3_p1-r3
- Alpine:v3.13: `openssh` — affected >=6.2 <8.4_p1-r4
- Alpine:v3.14: `openssh` — affected >=6.2 <8.6_p1-r3
- Alpine:v3.15: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.16: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.17: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.18: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.19: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.20: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.21: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.22: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.23: `openssh` — affected >=6.2 <8.8_p1-r0
- Alpine:v3.24: `openssh` — affected >=6.2 <8.8_p1-r0

## Details
sshd in OpenSSH 6.2 through 8.x before 8.8, when certain non-default configurations are used, allows privilege escalation because supplemental groups are not initialized as expected. Helper programs for AuthorizedKeysCommand and AuthorizedPrincipalsCommand may run with privileges associated with group memberships of the sshd process, if the configuration specifies running the command as a different user.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41617
