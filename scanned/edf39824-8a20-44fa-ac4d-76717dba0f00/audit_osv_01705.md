# [H] ALPINE-CVE-2020-10713

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-10713
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10713
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
A flaw was found in grub2, prior to version 2.06. An attacker may use the GRUB 2 flaw to hijack and tamper the GRUB verification process. This flaw also allows the bypass of Secure Boot protections. In order to load an untrusted or modified kernel, an attacker would first need to establish access to the system such as gaining physical access, obtain the ability to alter a pxe-boot network, or have remote access to a networked system with root access. With this access, an attacker could then craft a string to cause a buffer overflow by injecting a malicious payload that leads to arbitrary code execution within GRUB. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10713
