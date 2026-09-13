# [H] ALPINE-CVE-2020-14372

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14372
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14372
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
A flaw was found in grub2 in versions prior to 2.06, where it incorrectly enables the usage of the ACPI command when Secure Boot is enabled. This flaw allows an attacker with privileged access to craft a Secondary System Description Table (SSDT) containing code to overwrite the Linux kernel lockdown variable content directly into memory. The table is further loaded and executed by the kernel, defeating its Secure Boot lockdown and allowing the attacker to load unsigned code. The highest threat from this vulnerability is to data confidentiality and integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14372
