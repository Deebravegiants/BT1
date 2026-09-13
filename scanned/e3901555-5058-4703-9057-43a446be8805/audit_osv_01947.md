# [H] ALPINE-CVE-2020-29481

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-29481
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29481
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.14.1-r0

## Details
An issue was discovered in Xen through 4.14.x. Access rights of Xenstore nodes are per domid. Unfortunately, existing granted access rights are not removed when a domain is being destroyed. This means that a new domain created with the same domid will inherit the access rights to Xenstore nodes from the previous domain(s) with the same domid. Because all Xenstore entries of a guest below /local/domain/<domid> are being deleted by Xen tools when a guest is destroyed, only Xenstore entries of other guests still running are affected. For example, a newly created guest domain might be able to read sensitive information that had belonged to a previously existing guest domain. Both Xenstore implementations (C and Ocaml) are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29481
