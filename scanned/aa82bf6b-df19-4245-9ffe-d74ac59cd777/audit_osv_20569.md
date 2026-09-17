# [M] CVE-2021-3527

## Summary
Severity: Medium
Advisory: CVE-2021-3527
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-3527
Type: osv

## Details
A flaw was found in the USB redirector device (usb-redir) of QEMU. Small USB packets are combined into a single, large transfer request, to reduce the overhead and improve performance. The combined size of the bulk transfer is used to dynamically allocate a variable length array (VLA) on the stack without proper validation. Since the total size is not bounded, a malicious guest could use this flaw to influence the array length and cause the QEMU process to perform an excessive allocation on the stack, resulting in a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210708-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=1955695
- https://gitlab.com/qemu-project/qemu/-/commit/05a40b172e4d691371534828078be47e7fff524c
- https://gitlab.com/qemu-project/qemu/-/commit/7ec54f9eb62b5d177e30eb8b1cad795a5f8d8986
- https://www.openwall.com/lists/oss-security/2021/05/05/5
