# [M] ALPINE-CVE-2021-36158

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-36158
Ecosystem: Alpine:v3.11
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36158
Type: osv

## Affected
- Alpine:v3.11: `xrdp` — affected >=0 <0.9.11-r1

## Details
In the xrdp package (in branches through 3.14) for Alpine Linux, RDP sessions are vulnerable to man-in-the-middle attacks because pre-generated RSA certificates and private keys are used.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36158
