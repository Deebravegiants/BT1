# [M] CVE-2014-3471

## Summary
Severity: Medium
Advisory: CVE-2014-3471
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-12
Source: https://osv.dev/vulnerability/CVE-2014-3471
Type: osv

## Details
Use-after-free vulnerability in hw/pci/pcie.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (QEMU instance crash) via hotplug and hotunplug operations of Virtio block devices.

## References
- http://security.gentoo.org/glsa/glsa-201412-01.xml
- http://www.openwall.com/lists/oss-security/2014/06/23/4
- http://www.securityfocus.com/bid/68145
- https://bugzilla.redhat.com/show_bug.cgi?id=1112271
- https://lists.gnu.org/archive/html/qemu-devel/2014-06/msg05283.html
- http://www.openwall.com/lists/oss-security/2014/06/23/4
- http://www.openwall.com/lists/oss-security/2014/06/23/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1112271
- https://lists.gnu.org/archive/html/qemu-devel/2014-06/msg05283.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1112271
