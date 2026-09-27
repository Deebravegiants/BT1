# [M] CVE-2015-8568

## Summary
Severity: Medium
Advisory: CVE-2015-8568
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2015-8568
Type: osv

## Details
Memory leak in QEMU, when built with a VMWARE VMXNET3 paravirtual NIC emulator support, allows local guest users to cause a denial of service (host memory consumption) by trying to activate the vmxnet3 device repeatedly.

## References
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/15/10
- http://www.securityfocus.com/bid/79721
- https://bugzilla.redhat.com/show_bug.cgi?id=1289816
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02299.html
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/12/15/10
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02299.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1289816
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg02299.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1289816
