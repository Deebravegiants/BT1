# [M] ALPINE-CVE-2020-14145

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14145
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14145
Type: osv

## Affected
- Alpine:v3.12: `openssh` — affected >=5.7 <8.3_p1-r1
- Alpine:v3.13: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.14: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.15: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.16: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.17: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.18: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.19: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.20: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.21: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.22: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.23: `openssh` — affected >=5.7 <8.4_p1-r0
- Alpine:v3.24: `openssh` — affected >=5.7 <8.4_p1-r0

## Details
The client side in OpenSSH 5.7 through 8.4 has an Observable Discrepancy leading to an information leak in the algorithm negotiation. This allows man-in-the-middle attackers to target initial connection attempts (where no host key for the server has been cached by the client). NOTE: some reports state that 8.5 and 8.6 are also affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14145
