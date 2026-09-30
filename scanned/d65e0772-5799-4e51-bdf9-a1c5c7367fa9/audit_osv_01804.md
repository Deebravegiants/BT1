# [M] ALPINE-CVE-2020-15706

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15706
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15706
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
GRUB2 contains a race condition in grub_script_function_create() leading to a use-after-free vulnerability which can be triggered by redefining a function whilst the same function is already executing, leading to arbitrary code execution and secure boot restriction bypass. This issue affects GRUB2 version 2.04 and prior versions.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15706
