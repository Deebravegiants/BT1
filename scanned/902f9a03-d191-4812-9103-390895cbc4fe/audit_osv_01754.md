# [M] ALPINE-CVE-2020-14310

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14310
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14310
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
There is an issue on grub2 before version 2.06 at function read_section_as_string(). It expects a font name to be at max UINT32_MAX - 1 length in bytes but it doesn't verify it before proceed with buffer allocation to read the value from the font value. An attacker may leverage that by crafting a malicious font file which has a name with UINT32_MAX, leading to read_section_as_string() to an arithmetic overflow, zero-sized allocation and further heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14310
