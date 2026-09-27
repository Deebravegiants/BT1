# [H] ALPINE-CVE-2024-31145

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-31145
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-09-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31145
Type: osv

## Affected
- Alpine:v3.17: `xen` — affected >=4.0.0 <4.16.6-r1
- Alpine:v3.18: `xen` — affected >=4.0.0 <4.17.5-r0
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.18.3-r0
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.18.3-r0
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.19.0-r0
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.19.0-r0
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.19.0-r0
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.19.0-r0

## Details
Certain PCI devices in a system might be assigned Reserved Memory
Regions (specified via Reserved Memory Region Reporting, "RMRR") for
Intel VT-d or Unity Mapping ranges for AMD-Vi.  These are typically used
for platform tasks such as legacy USB emulation.

Since the precise purpose of these regions is unknown, once a device
associated with such a region is active, the mappings of these regions
need to remain continuouly accessible by the device.  In the logic
establishing these mappings, error handling was flawed, resulting in
such mappings to potentially remain in place when they should have been
removed again.  Respective guests would then gain access to memory
regions which they aren't supposed to have access to.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31145
