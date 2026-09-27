# [M] CVE-2021-36158

## Summary
Severity: Medium
Advisory: CVE-2021-36158
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-05
Source: https://osv.dev/vulnerability/CVE-2021-36158
Type: osv

## Details
In the xrdp package (in branches through 3.14) for Alpine Linux, RDP sessions are vulnerable to man-in-the-middle attacks because pre-generated RSA certificates and private keys are used.

## References
- https://gitlab.alpinelinux.org/alpine/aports/-/issues/12811
