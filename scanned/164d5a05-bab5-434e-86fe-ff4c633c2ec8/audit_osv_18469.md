# [M] CVE-2020-27821

## Summary
Severity: Medium
Advisory: CVE-2020-27821
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-27821
Type: osv

## Details
A flaw was found in the memory management API of QEMU during the initialization of a memory region cache. This issue could lead to an out-of-bounds write access to the MSI-X table while performing MMIO operations. A guest user may abuse this flaw to crash the QEMU process on the host, resulting in a denial of service. This flaw affects QEMU versions prior to 5.2.0.

## References
- http://www.openwall.com/lists/oss-security/2020/12/16/6
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20210115-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1902651
