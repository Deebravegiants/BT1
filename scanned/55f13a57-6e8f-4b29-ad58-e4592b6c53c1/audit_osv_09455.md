# [M] CVE-2016-9922

## Summary
Severity: Medium
Advisory: CVE-2016-9922
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2016-9922
Type: osv

## Details
The cirrus_do_copy function in hw/display/cirrus_vga.c in QEMU (aka Quick Emulator), when cirrus graphics mode is VGA, allows local guest OS privileged users to cause a denial of service (divide-by-zero error and QEMU process crash) via vectors involving blit pitch values.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=4299b90e9ba9ce5ca9024572804ba751aa1a7e70
- http://www.securityfocus.com/bid/94803
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.openwall.com/lists/oss-security/2016/12/09/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1334398
- https://lists.gnu.org/archive/html/qemu-devel/2016-12/msg00442.html
