# [M] CVE-2023-3773

## Summary
Severity: Medium
Advisory: CVE-2023-3773
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-3773
Type: osv

## Details
A flaw was found in the Linux kernel’s IP framework for transforming packets (XFRM subsystem). This issue may allow a malicious user with CAP_NET_ADMIN privileges to cause a 4 byte out-of-bounds read of XFRMA_MTIMER_THRESH when parsing netlink attributes, leading to potential leakage of sensitive heap data to userspace.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://access.redhat.com/security/cve/CVE-2023-3773
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:6583
- https://bugzilla.redhat.com/show_bug.cgi?id=2218944
