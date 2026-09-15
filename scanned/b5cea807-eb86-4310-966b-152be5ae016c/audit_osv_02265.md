# [H] ALPINE-CVE-2021-3697

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3697
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3697
Type: osv

## Affected
- Alpine:v3.15: `grub` — affected >=0 <2.06-r3
- Alpine:v3.16: `grub` — affected >=0 <2.06-r3
- Alpine:v3.17: `grub` — affected >=0 <2.06-r8
- Alpine:v3.18: `grub` — affected >=0 <2.06-r12
- Alpine:v3.19: `grub` — affected >=0 <2.06-r13
- Alpine:v3.20: `grub` — affected >=0 <2.06-r13
- Alpine:v3.21: `grub` — affected >=0 <2.06-r13
- Alpine:v3.22: `grub` — affected >=0 <2.06-r13
- Alpine:v3.23: `grub` — affected >=0 <2.06-r13
- Alpine:v3.24: `grub` — affected >=0 <2.06-r13

## Details
A crafted JPEG image may lead the JPEG reader to underflow its data pointer, allowing user-controlled data to be written in heap. To a successful to be performed the attacker needs to perform some triage over the heap layout and craft an image with a malicious format and payload. This vulnerability can lead to data corruption and eventual code execution or secure boot circumvention. This flaw affects grub2 versions prior grub-2.12.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3697
