# [H] ALPINE-CVE-2020-25632

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25632
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25632
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
A flaw was found in grub2 in versions prior to 2.06. The rmmod implementation allows the unloading of a module used as a dependency without checking if any other dependent module is still loaded leading to a use-after-free scenario. This could allow arbitrary code to be executed or a bypass of Secure Boot protections. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25632
