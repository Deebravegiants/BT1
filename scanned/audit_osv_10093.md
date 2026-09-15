# [M] CVE-2017-13672

## Summary
Severity: Medium
Advisory: CVE-2017-13672
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-13672
Type: osv

## Details
QEMU (aka Quick Emulator), when built with the VGA display emulator support, allows local guest OS privileged users to cause a denial of service (out-of-bounds read and QEMU process crash) via vectors involving display update.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- http://www.debian.org/security/2017/dsa-3991
- http://www.securityfocus.com/bid/100540
- https://access.redhat.com/errata/RHSA-2018:0816
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:1113
- https://access.redhat.com/errata/RHSA-2018:2162
- https://usn.ubuntu.com/3575-1/
- http://www.openwall.com/lists/oss-security/2017/08/30/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1486560
- https://lists.gnu.org/archive/html/qemu-devel/2017-08/msg04684.html
