# [M] ALPINE-CVE-2020-25596

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25596
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25596
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=3.2.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=3.2.0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. x86 PV guest kernels can experience denial of service via SYSENTER. The SYSENTER instruction leaves various state sanitization activities to software. One of Xen's sanitization paths injects a #GP fault, and incorrectly delivers it twice to the guest. This causes the guest kernel to observe a kernel-privilege #GP fault (typically fatal) rather than a user-privilege #GP fault (usually converted into SIGSEGV/etc.). Malicious or buggy userspace can crash the guest kernel, resulting in a VM Denial of Service. All versions of Xen from 3.2 onwards are vulnerable. Only x86 systems are vulnerable. ARM platforms are not vulnerable. Only x86 systems that support the SYSENTER instruction in 64bit mode are vulnerable. This is believed to be Intel, Centaur, and Shanghai CPUs. AMD and Hygon CPUs are not believed to be vulnerable. Only x86 PV guests can exploit the vulnerability. x86 PVH / HVM guests cannot exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25596
