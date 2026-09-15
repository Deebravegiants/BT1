# [H] CVE-2020-35517

## Summary
Severity: High
Advisory: CVE-2020-35517
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-01-28
Source: https://osv.dev/vulnerability/CVE-2020-35517
Type: osv

## Details
A flaw was found in qemu. A host privilege escalation issue was found in the virtio-fs shared file system daemon where a privileged guest user is able to create a device special file in the shared directory and use it to r/w access host devices.

## References
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210312-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1915823
- https://github.com/qemu/qemu/commit/ebf101955ce8f8d72fba103b5151115a4335de2c
- https://lists.gnu.org/archive/html/qemu-devel/2021-01/msg05461.html
- https://www.openwall.com/lists/oss-security/2021/01/22/1
