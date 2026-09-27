# [M] CVE-2017-5898

## Summary
Severity: Medium
Advisory: CVE-2017-5898
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5898
Type: osv

## Details
Integer overflow in the emulated_apdu_from_guest function in usb/dev-smartcard-reader.c in Quick Emulator (Qemu), when built with the CCID Card device emulator support, allows local users to cause a denial of service (application crash) via a large Application Protocol Data Units (APDU) unit.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=c7dfbf322595ded4e70b626bf83158a9f3807c6a
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00048.html
- http://www.securityfocus.com/bid/96112
- https://access.redhat.com/errata/RHSA-2017:1856
- https://access.redhat.com/errata/RHSA-2017:2392
- http://www.openwall.com/lists/oss-security/2017/02/07/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1419699
- https://security.gentoo.org/glsa/201702-28
