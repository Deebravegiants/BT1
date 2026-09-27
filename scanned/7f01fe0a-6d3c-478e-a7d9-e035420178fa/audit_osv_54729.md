# [H] CVE-2024-31145

## Summary
Severity: High
Advisory: CVE-2024-31145
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-09-25
Source: https://osv.dev/vulnerability/CVE-2024-31145
Type: osv

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
- http://www.openwall.com/lists/oss-security/2024/08/14/2
- https://xenbits.xenproject.org/xsa/advisory-460.html
- http://xenbits.xen.org/xsa/advisory-460.html
