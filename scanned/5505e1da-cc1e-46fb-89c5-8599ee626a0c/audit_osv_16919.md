# [M] CVE-2020-10717

## Summary
Severity: Medium
Advisory: CVE-2020-10717
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/CVE-2020-10717
Type: osv

## Details
A potential DoS flaw was found in the virtio-fs shared file system daemon (virtiofsd) implementation of the QEMU version >= v5.0. Virtio-fs is meant to share a host file system directory with a guest via virtio-fs device. If the guest opens the maximum number of file descriptors under the shared directory, a denial of service may occur. This flaw allows a guest user/process to cause this denial of service on the host.

## References
- https://lists.gnu.org/archive/html/qemu-devel/2020-05/msg00141.html
- https://security.gentoo.org/glsa/202011-09
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10717
- https://lists.gnu.org/archive/html/qemu-devel/2020-05/msg00143.html
- https://www.openwall.com/lists/oss-security/2020/05/04/1
