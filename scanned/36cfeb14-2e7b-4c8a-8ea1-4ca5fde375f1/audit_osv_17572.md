# [M] CVE-2020-1711

## Summary
Severity: Medium
Advisory: CVE-2020-1711
CVSS: 6.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2020-1711
Type: osv

## Details
An out-of-bounds heap buffer access flaw was found in the way the iSCSI Block driver in QEMU versions 2.12.0 before 4.2.1 handled a response coming from an iSCSI server while checking the status of a Logical Address Block (LBA) in an iscsi_co_block_status() routine. A remote user could use this flaw to crash the QEMU process, resulting in a denial of service or potential execution of arbitrary code with privileges of the QEMU process on the host.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00007.html
- https://access.redhat.com/errata/RHSA-2020:0669
- https://access.redhat.com/errata/RHSA-2020:0730
- https://access.redhat.com/errata/RHSA-2020:0731
- https://access.redhat.com/errata/RHSA-2020:0773
- https://lists.debian.org/debian-lts-announce/2020/03/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00013.html
- https://security.gentoo.org/glsa/202005-02
- https://usn.ubuntu.com/4283-1/
- https://www.openwall.com/lists/oss-security/2020/01/23/3
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1711
- https://lists.gnu.org/archive/html/qemu-devel/2020-01/msg05535.html
