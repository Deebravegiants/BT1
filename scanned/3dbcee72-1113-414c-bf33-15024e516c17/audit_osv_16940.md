# [M] CVE-2020-10761

## Summary
Severity: Medium
Advisory: CVE-2020-10761
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-10761
Type: osv

## Details
An assertion failure issue was found in the Network Block Device(NBD) Server in all QEMU versions before QEMU 5.0.1. This flaw occurs when an nbd-client sends a spec-compliant request that is near the boundary of maximum permitted request length. A remote nbd-client could use this flaw to crash the qemu-nbd server resulting in a denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00086.html
- https://security.gentoo.org/glsa/202011-09
- https://security.netapp.com/advisory/ntap-20200731-0001/
- https://usn.ubuntu.com/4467-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10761
- https://www.openwall.com/lists/oss-security/2020/06/09/1
