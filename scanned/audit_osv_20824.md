# [H] CVE-2021-3748

## Summary
Severity: High
Advisory: CVE-2021-3748
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-3748
Type: osv

## Details
A use-after-free vulnerability was found in the virtio-net device of QEMU. It could occur when the descriptor's address belongs to the non direct access region, due to num_buffers being set after the virtqueue elem has been unmapped. A malicious guest could use this flaw to crash QEMU, resulting in a denial of service condition, or potentially execute code on the host with the privileges of the QEMU process.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00002.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220425-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=1998514
- https://github.com/qemu/qemu/commit/bedd7e93d01961fcb16a97ae45d93acf357e11f6
- https://lists.nongnu.org/archive/html/qemu-devel/2021-09/msg00388.html
- https://ubuntu.com/security/CVE-2021-3748
