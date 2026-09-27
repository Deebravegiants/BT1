# [M] ALPINE-CVE-2019-19579

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19579
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19579
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.2-r0
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r2
- Alpine:v3.9: `xen` — affected >=0 <4.11.3-r0

## Details
An issue was discovered in Xen through 4.12.x allowing attackers to gain host OS privileges via DMA in a situation where an untrusted domain has access to a physical device (and assignable-add is not used), because of an incomplete fix for CVE-2019-18424. XSA-302 relies on the use of libxl's "assignable-add" feature to prepare devices to be assigned to untrusted guests. Unfortunately, this is not considered a strictly required step for device assignment. The PCI passthrough documentation on the wiki describes alternate ways of preparing devices for assignment, and libvirt uses its own ways as well. Hosts where these "alternate" methods are used will still leave the system in a vulnerable state after the device comes back from a guest. An untrusted domain with access to a physical device can DMA into host memory, leading to privilege escalation. Only systems where guests are given direct access to physical devices capable of DMA (PCI pass-through) are vulnerable. Systems which do not use PCI pass-through are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19579
