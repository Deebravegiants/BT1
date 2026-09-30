# [M] CVE-2023-26545

## Summary
Severity: Medium
Advisory: CVE-2023-26545
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26545
Type: osv

## Details
In the Linux kernel before 6.1.13, there is a double free in net/mpls/af_mpls.c upon an allocation failure (for registering the sysctl table under a new location) during the renaming of a device.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20230316-0009/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.13
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=fda6c89fe3d9aca073495a664e1d5aea28cd4377
- https://github.com/torvalds/linux/commit/fda6c89fe3d9aca073495a664e1d5aea28cd4377
