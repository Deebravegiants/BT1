# [M] ALPINE-CVE-2020-27749

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-27749
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27749
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
A flaw was found in grub2 in versions prior to 2.06. Variable names present are expanded in the supplied command line into their corresponding variable contents, using a 1kB stack buffer for temporary storage, without sufficient bounds checking. If the function is called with a command line that references a variable with a sufficiently large payload, it is possible to overflow the stack buffer, corrupt the stack frame and control execution which could also circumvent Secure Boot protections. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27749
