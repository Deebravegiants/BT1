# [M] CVE-2016-8909

## Summary
Severity: Medium
Advisory: CVE-2016-8909
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8909
Type: osv

## Details
The intel_hda_xfer function in hw/audio/intel-hda.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and CPU consumption) via an entry with the same value for buffer length and pointer position.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/24/4
- http://www.securityfocus.com/bid/93842
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/24/1
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg04682.html
