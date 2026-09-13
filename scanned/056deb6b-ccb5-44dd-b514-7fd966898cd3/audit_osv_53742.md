# [M] CVE-2023-2269

## Summary
Severity: Medium
Advisory: CVE-2023-2269
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2023-2269
Type: osv

## Details
A denial of service problem was found, due to a possible recursive locking scenario, resulting in a deadlock in table_clear in drivers/md/dm-ioctl.c in the Linux Kernel Device Mapper-Multipathing sub-component.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IXHBLWYNSUBS77TYPOJTADPDXKBH2F4U/
- https://www.debian.org/security/2023/dsa-5448
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/63AJUCJTZCII2JMAF7MGZEM66KY7IALT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FBLBKW2WM5YSTS6OGEU5SYHXSJ5EWSTV/
- https://lore.kernel.org/lkml/ZD1xyZxb3rHot8PV%40redhat.com/t/
- https://security.netapp.com/advisory/ntap-20230929-0004/
- https://www.debian.org/security/2023/dsa-5480
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
