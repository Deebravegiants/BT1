# [M] CVE-2018-7858

## Summary
Severity: Medium
Advisory: CVE-2018-7858
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2018-7858
Type: osv

## Details
Quick Emulator (aka QEMU), when built with the Cirrus CLGD 54xx VGA Emulator support, allows local guest OS privileged users to cause a denial of service (out-of-bounds access and QEMU process crash) by leveraging incorrect region calculation when updating VGA display.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- http://www.securityfocus.com/bid/103350
- https://access.redhat.com/errata/RHSA-2018:1369
- https://access.redhat.com/errata/RHSA-2018:1416
- https://access.redhat.com/errata/RHSA-2018:2162
- https://usn.ubuntu.com/3649-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1553402
- http://www.openwall.com/lists/oss-security/2018/03/09/1
- https://lists.nongnu.org/archive/html/qemu-devel/2018-03/msg02174.html
