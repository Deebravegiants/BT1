# [C] ALPINE-CVE-2023-28531

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-28531
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28531
Type: osv

## Affected
- Alpine:v3.16: `openssh` — affected >=8.9 <9.0_p1-r3
- Alpine:v3.17: `openssh` — affected >=8.9 <9.1_p1-r3

## Details
ssh-add in OpenSSH before 9.3 adds smartcard keys to ssh-agent without the intended per-hop destination constraints. The earliest affected version is 8.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28531
