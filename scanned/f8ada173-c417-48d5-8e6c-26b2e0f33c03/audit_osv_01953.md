# [M] ALPINE-CVE-2020-29566

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29566
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29566
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
An issue was discovered in Xen through 4.14.x. When they require assistance from the device model, x86 HVM guests must be temporarily de-scheduled. The device model will signal Xen when it has completed its operation, via an event channel, so that the relevant vCPU is rescheduled. If the device model were to signal Xen without having actually completed the operation, the de-schedule / re-schedule cycle would repeat. If, in addition, Xen is resignalled very quickly, the re-schedule may occur before the de-schedule was fully complete, triggering a shortcut. This potentially repeating process uses ordinary recursive function calls, and thus could result in a stack overflow. A malicious or buggy stubdomain serving a HVM guest can cause Xen to crash, resulting in a Denial of Service (DoS) to the entire host. Only x86 systems are affected. Arm systems are not affected. Only x86 stubdomains serving HVM guests can exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29566
