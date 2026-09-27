# [M] CVE-2019-11833

## Summary
Severity: Medium
Advisory: CVE-2019-11833
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-11833
Type: osv

## Details
fs/ext4/extents.c in the Linux kernel through 5.1.2 does not zero out the unused memory region in the extent tree block, which might allow local users to obtain sensitive information by reading uninitialized data in the filesystem.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GJGZIMGB72TL7OGWRMHIL43WHXFQWU4X/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://access.redhat.com/errata/RHSA-2019:2043
- https://access.redhat.com/errata/RHSA-2019:3309
- https://lists.debian.org/debian-lts-announce/2019/06/msg00010.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00011.html
- https://usn.ubuntu.com/4068-1/
- https://usn.ubuntu.com/4069-1/
- https://seclists.org/bugtraq/2019/Jun/26
- https://usn.ubuntu.com/4069-2/
- https://usn.ubuntu.com/4076-1/
- https://usn.ubuntu.com/4095-2/
- https://usn.ubuntu.com/4118-1/
- http://www.securityfocus.com/bid/108372
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:3517
- https://www.debian.org/security/2019/dsa-4465
