# [M] CVE-2016-2392

## Summary
Severity: Medium
Advisory: CVE-2016-2392
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-2392
Type: osv

## Details
The is_rndis function in the USB Net device emulator (hw/usb/dev-network.c) in QEMU before 2.5.1 does not properly validate USB configuration descriptor objects, which allows local guest OS administrators to cause a denial of service (NULL pointer dereference and QEMU process crash) via vectors involving a remote NDIS control message packet.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=80eecda8e5d09c442c24307f340840a5b70ea3b9
- http://www.openwall.com/lists/oss-security/2016/02/16/7
- http://www.securityfocus.com/bid/83274
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- http://lists.nongnu.org/archive/html/qemu-stable/2016-03/msg00064.html
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.gnu.org/archive/html/qemu-devel/2016-02/msg02553.html
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1302299
