# [M] CVE-2023-33951

## Summary
Severity: Medium
Advisory: CVE-2023-33951
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-33951
Type: osv

## Details
A race condition vulnerability was found in the vmwgfx driver in the Linux kernel. The flaw exists within the handling of GEM objects. The issue results from improper locking when performing operations on an object. This flaw allows a local privileged user to disclose information in the context of the kernel.

## References
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/errata/RHSA-2023:6901
- https://access.redhat.com/errata/RHSA-2024:1404
- https://access.redhat.com/errata/RHSA-2024:4823
- https://access.redhat.com/errata/RHSA-2024:4831
- https://access.redhat.com/security/cve/CVE-2023-33951
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-20110/
- https://access.redhat.com/errata/RHSA-2023:7077
- https://bugzilla.redhat.com/show_bug.cgi?id=2218195
