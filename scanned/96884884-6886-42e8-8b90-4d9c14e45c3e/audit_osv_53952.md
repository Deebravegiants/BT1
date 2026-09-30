# [M] CVE-2023-33952

## Summary
Severity: Medium
Advisory: CVE-2023-33952
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-33952
Type: osv

## Details
A double-free vulnerability was found in handling vmw_buffer_object objects in the vmwgfx driver in the Linux kernel. This issue occurs due to the lack of validating the existence of an object prior to performing further free operations on the object, which may allow a local privileged user to escalate privileges and execute code in the context of the kernel.

## References
- https://access.redhat.com/errata/RHSA-2023:7077
- https://access.redhat.com/errata/RHSA-2024:1404
- https://access.redhat.com/errata/RHSA-2024:4831
- https://access.redhat.com/security/cve/CVE-2023-33952
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/errata/RHSA-2023:6901
- https://access.redhat.com/errata/RHSA-2024:4823
- https://bugzilla.redhat.com/show_bug.cgi?id=2218212
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-20292
