# [H] ALPINE-CVE-2020-25595

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25595
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25595
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. The PCI passthrough code improperly uses register data. Code paths in Xen's MSI handling have been identified that act on unsanitized values read back from device hardware registers. While devices strictly compliant with PCI specifications shouldn't be able to affect these registers, experience shows that it's very common for devices to have out-of-spec "backdoor" operations that can affect the result of these reads. A not fully trusted guest may be able to crash Xen, leading to a Denial of Service (DoS) for the entire system. Privilege escalation and information leaks cannot be excluded. All versions of Xen supporting PCI passthrough are affected. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only guests with passed through PCI devices may be able to leverage the vulnerability. Only systems passing through devices with out-of-spec ("backdoor") functionality can cause issues. Experience shows that such out-of-spec functionality is common; unless you have reason to believe that your device does not have such functionality, it's better to assume that it does.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25595
