# [H] ALPINE-CVE-2022-42309

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42309
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42309
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r6
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.17: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.18: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.19: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.20: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.21: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.22: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.23: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.24: `xen` — affected >=0 <4.16.2-r1

## Details
Xenstore: Guests can crash xenstored Due to a bug in the fix of XSA-115 a malicious guest can cause xenstored to use a wrong pointer during node creation in an error path, resulting in a crash of xenstored or a memory corruption in xenstored causing further damage. Entering the error path can be controlled by the guest e.g. by exceeding the quota value of maximum nodes per domain.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42309
