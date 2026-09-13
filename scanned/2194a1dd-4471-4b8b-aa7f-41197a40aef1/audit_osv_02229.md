# [M] ALPINE-CVE-2021-3418

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3418
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3418
Type: osv

## Affected
- Alpine:v3.17: `grub` — affected >=0 <2.06-r0
- Alpine:v3.18: `grub` — affected >=0 <2.06-r0
- Alpine:v3.19: `grub` — affected >=0 <2.06-r0
- Alpine:v3.20: `grub` — affected >=0 <2.06-r0
- Alpine:v3.21: `grub` — affected >=0 <2.06-r0
- Alpine:v3.22: `grub` — affected >=0 <2.06-r0
- Alpine:v3.23: `grub` — affected >=0 <2.06-r0
- Alpine:v3.24: `grub` — affected >=0 <2.06-r0

## Details
If certificates that signed grub are installed into db, grub can be booted directly. It will then boot any kernel without signature validation. The booted kernel will think it was booted in secureboot mode and will implement lockdown, yet it could have been tampered. This flaw is a reintroduction of CVE-2020-15705 and only affects grub2 versions prior to 2.06 and upstream and distributions using the shim_lock mechanism.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3418
