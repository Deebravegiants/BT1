# [M] CVE-2017-7718

## Summary
Severity: Medium
Advisory: CVE-2017-7718
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2017-7718
Type: osv

## Details
hw/display/cirrus_vga_rop.h in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (out-of-bounds read and QEMU process crash) via vectors related to copying VGA data via the cirrus_bitblt_rop_fwd_transp_ and cirrus_bitblt_rop_fwd_ functions.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=215902d7b6fb50c6fc216fc74f770858278ed904
- http://www.securityfocus.com/bid/97957
- https://access.redhat.com/errata/RHSA-2017:0980
- https://access.redhat.com/errata/RHSA-2017:0981
- https://access.redhat.com/errata/RHSA-2017:0982
- https://access.redhat.com/errata/RHSA-2017:0983
- https://access.redhat.com/errata/RHSA-2017:0984
- https://access.redhat.com/errata/RHSA-2017:0988
- https://access.redhat.com/errata/RHSA-2017:1205
- https://access.redhat.com/errata/RHSA-2017:1206
- https://access.redhat.com/errata/RHSA-2017:1430
- https://access.redhat.com/errata/RHSA-2017:1431
- https://access.redhat.com/errata/RHSA-2017:1441
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/04/19/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1443441
